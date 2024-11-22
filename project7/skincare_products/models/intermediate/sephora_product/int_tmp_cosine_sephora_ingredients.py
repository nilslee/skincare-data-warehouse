import json
import vertexai
import ast
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
from google.cloud import bigquery
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

# Project and model configuration
project_id = "segfault-434120"
region = "us-central1"
model_name = "gemini-1.5-flash-001"

# Template for ingredient standardization
prompt_template = """
Given a list of Sephora_Ingredient values, find the most similar Cosmetic_Ingredient from the provided list.
If a similar name is found, replace the Sephora ingredient with it; otherwise, replace it with null.
Return the result as a JSON object with the schema: current_value:string, new_value:string.
Only include objects for names that have been changed or mapped to null.
Do not include unchanged values in the response.

Sephora_Ingredients:
{}

Cosmetic Ingredients:
{}
"""

# SQL queries
cosmetic_ingredient_sql = """
SELECT DISTINCT
  LOWER(TRIM(REGEXP_REPLACE(ingredient_unique_name, r'[^a-zA-Z\s]', ''))) AS ingredient
FROM inc_skincare_products_stg.stg_cosmetic_ingredient
ORDER BY ingredient
"""

sephora_ingredient_sql = """
WITH flattened_ingredients AS (
  SELECT
    LOWER(TRIM(REGEXP_REPLACE(ingredient_part, r'[^a-zA-Z\s]', ''))) AS ingredient
  FROM
    inc_skincare_products_stg.stg_sephora_product,
    UNNEST(ingredients) AS ingredient,
    UNNEST(SPLIT(ingredient, ',')) AS ingredient_part
  WHERE
    ingredients IS NOT NULL
)
SELECT DISTINCT ingredient
FROM flattened_ingredients
ORDER BY ingredient
"""

# VertexAI Inference Function
def do_inference(sephora_ingredients, cosmetic_ingredients):
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(
        model_name,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        }
    )
    
    formatted_prompt = prompt_template.format(sephora_ingredients, cosmetic_ingredients)
    resp = model.generate_content(formatted_prompt)
    resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
    print("resp_text:", resp_text[:200])

    try:
        categories_dict = json.loads(resp_text)
        return [{"current_value": item["current_value"], "new_value": item["new_value"]} for item in categories_dict]
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        return []

# UDF for Updating Ingredients
def update_ingredients(ingredients_str, replacements_dict):
    try:
        ingredients_list = ast.literal_eval(ingredients_str)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing ingredients: {e}")
        return ingredients_str
    
    updated_ingredients = [replacements_dict.get(ingredient, ingredient) for ingredient in ingredients_list]
    return str(updated_ingredients)

# Main Function
def model(dbt, session):
    dbt.config(incremental_strategy="insert_overwrite")
    dbt.config(unique_key="ingredient")
    
    bq_client = bigquery.Client()
    cosmetic_rows = bq_client.query(cosmetic_ingredient_sql).result()
    sephora_rows = bq_client.query(sephora_ingredient_sql).result()

    cosmetic_ingredients = [row["ingredient"] for row in cosmetic_rows]
    sephora_ingredients = [row["ingredient"] for row in sephora_rows]
    cosmetic_ingredient_str = '\n'.join([ingredient for ingredient in cosmetic_ingredients if ingredient is not None])

    if dbt.is_incremental:
        print("is_incremental is true")
        max_load_time_query = f"SELECT MAX(_load_time) FROM {dbt.this}"
        max_load_time = session.sql(max_load_time_query).collect()[0][0]
        sephora_df = dbt.ref("stg_sephora_product_snp").filter(F.col("_load_time") >= max_load_time)
    else:
        print("is_incremental is false")
        sephora_df = dbt.ref("stg_sephora_product_snp")

    if sephora_df.count() == 0:
        print("No Sephora ingredients to process. Returning an empty DataFrame.")
        return session.createDataFrame([], schema="name: string, new_value: string")

    batch_size = 10
    combined_results = []
    for i in range(0, len(sephora_ingredients), batch_size):
        batch = sephora_ingredients[i:i + batch_size]
        sephora_ingredient_str = '\n'.join(batch)


        try:
            replacements = do_inference(sephora_ingredient_str, cosmetic_ingredient_str)
            combined_results.extend(replacements)
        except ValueError as e:
            print(f"Error processing batch {i}: {e}")
            continue

    print("combined_results:", combined_results[:100])

    replacements_dict = {item['current_value']: item['new_value'] for item in combined_results}
    update_ingredients_udf = F.udf(lambda x: update_ingredients(x, replacements_dict), StringType())
    output_df = sephora_df.withColumn("ingredients", update_ingredients_udf(F.col("ingredients")))

    return output_df
