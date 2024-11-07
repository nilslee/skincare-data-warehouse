import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold
from google.cloud import bigquery

# Set up project and model information
region = "us-central1"
model_name = "gemini-1.5-flash-001"

# Create a prompt for Gemini
prompt_template = """
Given a list of skin_condition_name values, find the most similar dermatologic_name from the provided list.
If a similar name is found, replace the skin_condition_name with it; otherwise, replace it with null.
Return a JSON array of objects, each containing "current_value" and "new_value".
Only include objects for names that have been changed or mapped to null.

Skin Condition Names:
{}

Dermatologic Names:
{}
"""

# Function for inference using Vertex AI
def do_inference(skin_condition_names, dermatologic_names):
    vertexai.init(location=region)
    model = GenerativeModel(model_name, safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        })
    
    all_replacements = {}

    for i in range(0, len(skin_condition_names), 10):  # Processing in chunks of 10
        chunk = skin_condition_names[i:i + 10]
        skin_condition_name_str = '\n'.join(chunk)
        final_prompt = prompt_template.format(skin_condition_name_str, ', '.join(dermatologic_names))

        # Generate content using the model
        resp = model.generate_content([final_prompt])
        resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
        print(f"Raw response for chunk {i}:", resp_text)

        try:
            mappings = json.loads(resp_text)
            for mapping in mappings:
                old = mapping.get("current_value")
                new = mapping.get("new_value")
                if old != new:
                    all_replacements[old] = new
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for chunk {i}: {e}")
            print("Response was:", resp_text)

    return all_replacements

# Main dbt model function
def model(dbt, session):
    # Initialize BigQuery client
    bq_client = bigquery.Client()

    # Query to get distinct skin condition names
    skin_condition_name_sql = "SELECT DISTINCT skin_condition_name FROM dbt_skincare_products_stg.skin_disease_picture WHERE skin_condition_name IS NOT NULL ORDER BY skin_condition_name"
    skin_condition_rows = bq_client.query(skin_condition_name_sql).result()
    skin_condition_name_list = [row["skin_condition_name"] for row in skin_condition_rows]

    # Query to get distinct dermatologic disease names
    dermatologic_names_sql = "SELECT DISTINCT name FROM dbt_skincare_products_stg.dermatologic_disease ORDER BY name"
    dermatologic_rows = bq_client.query(dermatologic_names_sql).result()
    dermatologic_name_list = [row["name"] for row in dermatologic_rows]

    # Process names and get replacements
    replacements = do_inference(skin_condition_name_list, dermatologic_name_list)
    print("Replacements:", replacements)

    # Retrieve original DataFrame from dbt reference
    df = dbt.ref("skin_disease_picture")

    # Replace skin_condition_name using replacements mapping
    output_df = df.na.replace(replacements, "skin_condition_name")

    return output_df
