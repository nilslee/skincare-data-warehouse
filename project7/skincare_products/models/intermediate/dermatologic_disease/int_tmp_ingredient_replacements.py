import json
import numpy as np
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
from pyspark.sql import Row
import concurrent.futures


project_id = "segfault-434120"
region = "us-central1"
dataset_id = "skincare_products_int"
model_name = "gemini-1.5-flash-001"
prompt = """I provided you with a list of official ingredient names and unofficial ingredient names. Go through the list of unofficial ingredients and look for official ingredients that have similar meanings, but have different names.
For example, 'aloe' and 'Hydrolyzed Aloe Barbadensis Leaf' have similar meanings and 'acetic acid' and 'ACETIC ACID' have similar meanings.
If an unofficial ingredient name is a broad category (e.g., drug classes, groups like 'antihistamines' or 'antibiotics'), do not select an unrelated individual ingredient. Instead, map it to the most common or relevant specific ingredient within that category if one exists.
For example, 'alpha-hydroxy acids' and 'glycolic acid'.
Avoid selecting unrelated ingredients. If no specific official ingredient matches (e.g., a general category or pharmaceutical ingredient), set new ingredient to null instead of a random match.
For example, if 'antihistamines' cannot be matched to a specific cosmetic ingredient, the result should be {"current_ingredient": "antihistamines", "new_ingredient": null}
Mapping the unoffical ingredient name to the official ingredient name.
Return the list of original ingredient names along with their new ingredient names.
Format the results as a JSON array with the schema: current_ingredient:string, new_ingredient:string.
Ensure special characters like quotes in the strings are properly escaped.
Do not leave trailing commas that would invalidate the JSON object.
Do not include an explanation with your answer.
The output format should look like this:
[{"current_ingredient": "glycolic acid", "new_ingredient": "glycolic acid"}, {"current_ingredient": "Benzoyl-peroxide", "new_ingredient": "benzoyl peroxide"}]    
"""

# Initialize Vertex AI model
def initialize_model():
    project_id = "segfault-434120"
    region = "us-central1"
    model_name = "gemini-1.5-flash-001"
    vertexai.init(project=project_id, location=region)
    return GenerativeModel(model_name)

# Find official ingredient name replacements
def process_ingredient_batch(model, official_ingredients, unofficial_ingredients):
    official_ingredient_str = 'Official Ingredient List: ' + ', '.join(official_ingredients)
    unofficial_ingredient_str = 'Unofficial Ingredient List: ' + ', '.join(unofficial_ingredients)

    resp = model.generate_content(contents=[official_ingredient_str, unofficial_ingredient_str, prompt], safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                })
    resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
    print("llm response: " + resp_text)
    ingredients = json.loads(resp_text)

    # ingredients can be either a dictionary or list type (depending on what LLM decides to do!)
    replacements = {}
    for entry in ingredients:
        if entry['new_ingredient'] is not None and entry['new_ingredient'].lower() != "null":
            replacements[entry['current_ingredient'].lower()] = entry['new_ingredient'].lower()

    return replacements


def model(dbt, session):
    dbt.config(incremental_strategy = "insert_overwrite")
    dbt.config(unique_key = "id")

    # Retrieve unofficial ingredient names 
    unofficial_name_input_df = dbt.ref("int_tmp_treatment_ingredient_unofficial_names")
    unofficial_ingredient_list = unofficial_name_input_df.select("ingredient").rdd.flatMap(lambda x: x).collect()

    # Retrieve official ingredient names and divide into batches
    official_name_input_df = dbt.ref("int_tmp_ingredient_official_names")
    official_ingredient_list = official_name_input_df.select("ingredient_unique_name").rdd.flatMap(lambda x: x).collect()
    print(f"official_ingredient_list: {official_ingredient_list}")

    # use the is_incremental macro to detect if this is the first run (i.e. we're creating the table)
    # or a subsequent run (i.e. we're upserting into the existing table)
    if dbt.is_incremental:
        print("is_incremental is true")
        max_from_this = f"select max(_load_time) from {dbt.this}"
        rows = official_name_input_df
        rows = rows.filter(rows._load_time >= session.sql(max_from_this).collect()[0][0])
    else:
        print("is_incremental is false")

    # Calculate batch size
    TOTAL_BATCHES = 10000
    print("total_batches:", TOTAL_BATCHES)
    official_ingredient_batches = np.array_split(official_ingredient_list, TOTAL_BATCHES)
    print(f"official_ingredient_batches: {official_ingredient_batches}")

    # Initialize model and replacements dictionary
    model = initialize_model()
    replacements = {}
    finished_count = 0

    # Process batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_ingredient_batch, model, batch, unofficial_ingredient_list) for batch in official_ingredient_batches]

        for future in concurrent.futures.as_completed(futures):
            try:
                batch_replacements = future.result()
                finished_count += 1
                print(f"{finished_count}/{TOTAL_BATCHES}: {batch_replacements}")
                replacements.update(batch_replacements)

            except Exception as e:
                print(f"Error processing chunk: {e}")

    # Log replaced ingredients and missing ingredients
    replaced_ingredients = set(replacements.keys())
    missing_ingredient_replacements = set([ingredient.lower() for ingredient in unofficial_ingredient_list]) - replaced_ingredients
    print(f"{len(replaced_ingredients)} replaced: {replaced_ingredients}")
    print(f"{len(missing_ingredient_replacements)} missing ingredients: {missing_ingredient_replacements}")

    # Create table with replacement dictionary
    row_data = [Row(old_ingredient=key, new_ingredient=value) for key, value in replacements.items()]
    df = session.createDataFrame(row_data)

    return df
