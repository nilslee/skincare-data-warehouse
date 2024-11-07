import json
import vertexai
import ast
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery
from pyspark.sql import Row
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

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
def do_inference(input_str):
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(model_name)
    resp = model.generate_content([input_str, prompt])
    resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
    print("resp_text:", resp_text[:100])

    # Parse the response to JSON format
    categories_dict = json.loads(resp_text)
    # Convert it to a list of Row objects with current_value and new_value
    categories = [{"current_value": k, "new_value": v} for k, v in categories_dict.items()]

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
    # Fetch distinct ingredients
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
            except ValueError as ve:
                print(f"Content moderation error on chunk {i}: {ve}")
                continue

            combined_results.extend(replacements)
            ingredients = []

    if ingredients:
        print("Processing last batch")
        ingredient_str = '\n'.join(ingredients)
        try:
            replacements = do_inference(ingredient_str)
        except ValueError as ve:
            print(f"Content moderation error on chunk {i}: {ve}")
        combined_results.extend(replacements)

    print("combined_results:", combined_results[:100])

    # Convert combined_results into a dictionary for fast lookup
    replacements_dict = {item['current_value']: item['new_value'] for item in combined_results}
    
    # Register the update_ingredients function as a UDF
    update_ingredients_udf = F.udf(lambda x: update_ingredients(x, replacements_dict), StringType())
    
    # Apply the UDF to the ingredients column
    sephora_df = dbt.source("skincare_products_raw", "sephora_product")
    output_df = sephora_df.withColumn("ingredients", update_ingredients_udf(F.col("ingredients")))
    
    return output_df

