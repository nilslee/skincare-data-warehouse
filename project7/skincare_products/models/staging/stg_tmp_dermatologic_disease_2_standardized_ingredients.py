import json
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
from pyspark.sql.functions import udf, explode, regexp_replace, split, broadcast
from pyspark.sql.types import ArrayType, StringType

# Initialize Vertex AI model
def initialize_model():
    project_id = "segfault-434120"
    region = "us-central1"
    model_name = "gemini-1.5-flash-001"
    vertexai.init(project=project_id, location=region)
    return GenerativeModel(model_name)

# Process a single batch of ingredients
def process_ingredients_batch(model, ingredients_str):
    prompt = """Go through this list of ingredients and look for ingredients that have similar meanings but different names.
    Format the results as an array of JSON objects with the schema: current_ingredient:string, new_ingredient:string.
    The output format should look like this:
    [{"current_ingredient": "hydrocortisone", "new_ingredient": "corticosteroid"}, {"current_ingredient": "intralesional interferon-alfa", "new_ingredient": "injected steroids"}]
    """

    resp = model.generate_content([ingredients_str, prompt], safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    })
    
    resp_text = resp.text.replace("```json", "").replace("```", "").strip()
    print(resp_text)
    
    # Parse the JSON content
    try:
        parsed = json.loads(resp_text)
        return {entry['current_ingredient']: entry['new_ingredient'] for entry in parsed}
    except json.JSONDecodeError:
        print("Error decoding JSON in batch response.")
        return {}

# Process ingredients in batches to avoid token limit issues
def process_ingredients_in_batches(ingredients_list, batch_size=50):
    model = initialize_model()
    replacements = {}

    # Split ingredients into batches and process each
    for i in range(0, len(ingredients_list), batch_size):
        batch = ingredients_list[i:i + batch_size]
        ingredients_str = "\n".join(batch)
        
        # Process the batch and update replacements
        batch_replacements = process_ingredients_batch(model, ingredients_str)
        replacements.update(batch_replacements)
    
    return replacements

# Register UDF for replacing ingredients
def replace_ingredients(treatments, replacements_dict):
    # Access the broadcasted dictionary
    return [replacements_dict.value.get(ingredient, ingredient) for ingredient in treatments]

replace_ingredients_udf = udf(replace_ingredients, ArrayType(StringType()))

# Convert dictionary to a broadcast variable in Spark
def model(dbt, session):
    dbt.config(incremental_strategy = "insert_overwrite")
    dbt.config(unique_key = "id")

    # Load the previous temp table
    ingredient_df = dbt.ref("stg_tmp_dermatologic_disease_1_processed_treatments")

    # Convert `treatments` string to array
    ingredient_df = ingredient_df.withColumn(
        "treatments_array",
        split(
            regexp_replace(
                regexp_replace("treatments", r'^\["|"\]$', ""),  # Remove leading/trailing brackets
                r'", "', ","  # Replace `", "` with comma
            ),
            ",\s*"  # Split by comma with optional spaces
        )
    )

    # Collect distinct ingredients
    ingredients = ingredient_df.select(explode("treatments_array").alias("ingredient")).distinct()
    ingredients_list = [row["ingredient"] for row in ingredients.collect()]

    # Process ingredients in batches
    replacements = process_ingredients_in_batches(ingredients_list)
    print("replacements:")
    print(replacements)

    # Broadcast the replacements dictionary
    replacements_broadcast = session.sparkContext.broadcast(replacements)

    # Register the UDF with broadcasted replacements
    replace_ingredients_udf = udf(lambda treatments: replace_ingredients(treatments, replacements_broadcast), ArrayType(StringType()))
    
    # Apply UDF to replace ingredients
    ingredient_df = ingredient_df.withColumn("treatments", replace_ingredients_udf("treatments_array"))

    # Drop the temporary treatments_array column if no longer needed
    ingredient_df = ingredient_df.drop("treatments_array")

    return ingredient_df