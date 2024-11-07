import json
import vertexai
import ast
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
from google.cloud import bigquery
from pyspark.sql import Row
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

# SQL query to retrieve distinct cosmetic ingredients
cosmetic_ingredient_sql = """
SELECT DISTINCT
  LOWER(TRIM(REGEXP_REPLACE(ingredient_unique_name, r'[^a-zA-Z\s]', ''))) AS ingredient
FROM dbt_skincare_products_stg.cosmetic_ingredient
ORDER BY ingredient
"""

# SQL query to retrieve distinct Sephora ingredients
sephora_ingredient_sql = """
WITH flattened_ingredients AS (
  SELECT
    LOWER(TRIM(REGEXP_REPLACE(ingredient_part, r'[^a-zA-Z\s]', ''))) AS ingredient
  FROM
    dbt_skincare_products_stg.sephora_product,
    UNNEST(ingredients) AS ingredient,
    UNNEST(SPLIT(ingredient, ',')) AS ingredient_part
  WHERE
    ingredients IS NOT NULL
)
SELECT DISTINCT ingredient
FROM flattened_ingredients
ORDER BY ingredient;
"""

spark.conf.set("spark.sql.debug.maxToStringFields", 2000)


# Parsing response to JSON as a list of dictionaries with the correct structure
def do_inference(sephora_ingredients, cosmetic_ingredients):
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(model_name, safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        })
      
    # Format the prompt with Sephora and Cosmetic ingredients
    formatted_prompt = prompt_template.format(sephora_ingredients, cosmetic_ingredients)
    resp = model.generate_content(formatted_prompt)
    resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
    print("resp_text:", resp_text[:200])

    # Parse the response to JSON format
    categories_dict = json.loads(resp_text)

    categories = [{"current_value": k, "new_value": v} for k, v in categories_dict.items()]
    # categories = [{"current_value": item["current_value"], "new_value": item["new_value"]} for item in categories_dict]

    return categories


def update_ingredients(ingredients_str, replacements_dict):
    # Convert the ingredients string to a list using ast.literal_eval
    try:
        ingredients_list = ast.literal_eval(ingredients_str)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing ingredients: {e}")
        return ingredients_str  # Return original string if parsing fails
    
    # Replace each ingredient in the list using the replacements dictionary
    updated_ingredients = [
        replacements_dict.get(ingredient, ingredient) for ingredient in ingredients_list
    ]
    
    # Convert the list back to a string format
    return str(updated_ingredients)

# Main function to standardize ingredients
def model(dbt, session):
    # Fetch distinct cosmetic and Sephora ingredients
    bq_client = bigquery.Client()
    cosmetic_rows = bq_client.query_and_wait(cosmetic_ingredient_sql)
    sephora_rows = bq_client.query_and_wait(sephora_ingredient_sql)

    cosmetic_ingredients = [row["ingredient"] for row in cosmetic_rows]
    sephora_ingredients = [row["ingredient"] for row in sephora_rows]
    cosmetic_ingredient_str = '\n'.join([ingredient for ingredient in cosmetic_ingredients if ingredient is not None])

    # Batch processing for Sephora ingredients
    batch_size = 10
    combined_results = []

    for i in range(0, len(sephora_ingredients), batch_size):
        batch = sephora_ingredients[i:i+batch_size]
        sephora_ingredient_str = '\n'.join(batch)
        try:
            replacements = do_inference(sephora_ingredient_str, cosmetic_ingredient_str)
        except ValueError as ve:
            print(f"Content moderation error on chunk {i}: {ve}")
            continue

        combined_results.extend(replacements)

    print("combined_results:", combined_results[:100])

    # Convert combined_results into a dictionary for fast lookup
    replacements_dict = {item['current_value']: item['new_value'] for item in combined_results}
    
    # Register the update_ingredients function as a UDF
    update_ingredients_udf = F.udf(lambda x: update_ingredients(x, replacements_dict), StringType())
    
    # Apply the UDF to the ingredients column
    sephora_df = dbt.ref("sephora_product")
    output_df = sephora_df.withColumn("ingredients", update_ingredients_udf(F.col("ingredients")))
    
    return output_df
