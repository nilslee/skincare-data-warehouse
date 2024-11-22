import json
import vertexai
import ast
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery
from pyspark.sql import Row
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

# Project and model configuration
project_id = "segfault-434120"
region = "us-central1"
model_name = "gemini-1.5-flash-001"

# Prompt to standardize ingredient names
prompt = """
Go through this list of ingredients and identify those with similar meanings but different names.
For example, 'alpha-hydroxy acid' and 'alpha hydroxyacids' could both be standardized to 'alpha hydroxyacid'.
Suggest a standard value, mapping each unique current ingredient to its new standardized name.
Some names are product names rather than ingredient names, so map them to an empty string.
For example, 'your skin but better setting spray', 'you’re my sol mate', and 'witch hazel & yucca deep hydrating shampoo' should all be mapped to ('').
Return the result as a JSON object with the schema: current_value:string, new_value:string.
Do not include unchanged values in the response.
"""

# SQL query to retrieve distinct ingredients
product_ingredients_sql = """
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
ORDER BY ingredient;
"""

# Parsing response to JSON as a list of dictionaries with the correct structure
def do_inference(input_str):
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(model_name)
    resp = model.generate_content([input_str, prompt])
    resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
    print("resp_text:", resp_text[:100])

    try:
        categories_dict = json.loads(resp_text)
    except Exception as e:
        print(f"Error while parsing JSON: {e}. Response: {resp_text}")
        return []

    categories = [{"current_value": k, "new_value": v} for k, v in categories_dict.items()]
    return categories

def update_ingredients(ingredients_str, replacements_dict):
    try:
        ingredients_list = ast.literal_eval(ingredients_str)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing ingredients: {e}")
        return ingredients_str  # Return original string if parsing fails
    
    updated_ingredients = [
        replacements_dict.get(ingredient, ingredient) for ingredient in ingredients_list
    ]
    return str(updated_ingredients)

# Main function to standardize ingredients
def model(dbt, session):
    dbt.config(incremental_strategy="insert_overwrite")
    dbt.config(unique_key="ingredient")

    # Check for incremental run
    sephora_df = dbt.ref("raw_sephora_products_snp")
    if dbt.is_incremental:
        print("Incremental run detected")
        max_load_time_query = f"SELECT MAX(_load_time) FROM {dbt.this}"
        max_load_time = session.sql(max_load_time_query).collect()[0][0]
        sephora_df = sephora_df.filter(F.col("_load_time") >= max_load_time)
    else:
        print("Full refresh detected")

    bq_client = bigquery.Client()
    rows = bq_client.query_and_wait(product_ingredients_sql)

    batch_size = 10
    ingredients = []
    combined_results = []

    for i, row in enumerate(rows):
        ingredients.append(row["ingredient"])

        if i > 0 and i % batch_size == 0:
            print("Processing batch")
            ingredient_str = '\n'.join(ingredients)
            try:
                replacements = do_inference(ingredient_str)
            except Exception as e:
                print(f"Error processing batch {i}: {e}")
                continue

            combined_results.extend(replacements)
            ingredients = []

    if ingredients:
        print("Processing last batch")
        ingredient_str = '\n'.join(ingredients)
        try:
            replacements = do_inference(ingredient_str)
        except Exception as e:
            print(f"Error processing last batch: {e}")
        combined_results.extend(replacements)

    print("combined_results:", combined_results[:100])

    if not combined_results:
        print("No results, returning an empty DataFrame")
        return session.createDataFrame(data=[], schema="current_value: string, new_value: string")

    replacements_dict = {item['current_value']: item['new_value'] for item in combined_results}
    update_ingredients_udf = F.udf(lambda x: update_ingredients(x, replacements_dict), StringType())

    output_df = sephora_df.withColumn("ingredients", update_ingredients_udf(F.col("ingredients")))
    return output_df
