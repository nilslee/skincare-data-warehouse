import json
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery

project_id = "segfault-434120"
region = "us-central1"
model_name = "gemini-1.5-flash-001"
prompt = """
Go through this list of skin_condition_name values and look for values that have similar meanings but were given different names.
For example, 'rosacea', 'acne rosacea', and 'rosacea (acne)' could all be standardized to 'rosacea'.
Suggest a standard value, mapping the current one to the new one.
Return the list of original values along with their new values.
Format the results as a json object with the schema: current_value:string, new_value:string.
Do not include any unchanged values in your answer.
Do not include an explanation with your answer.
"""

skin_condition_name_sql = """select distinct skin_condition_name from dbt_skincare_products_stg.skin_disease_picture where skin_condition_name is not null order by skin_condition_name"""

def do_inference(input_str):
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(model_name)
    resp = model.generate_content([input_str, prompt])
    resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
    print("resp_text:", resp_text)

    categories = json.loads(resp_text)
    replacements = {}

    if type(categories) == dict:
        for old, new in categories.items():
            if old != new:
                replacements[old] = new

    elif type(categories) == list:
        for cat_entry in categories:
            if cat_entry['current_value'] != cat_entry['new_value']:
                replacements[cat_entry['current_value']] = cat_entry['new_value']

    return replacements


def model(dbt, session):    

    bq_client = bigquery.Client()
    rows = bq_client.query_and_wait(skin_condition_name_sql)

    batch_size = 500
    skin_conditions = []
    combined_replacements = {}

    for i, row in enumerate(rows):
        skin_conditions.append(row["skin_condition_name"])

        if i > 0 and i % batch_size == 0:
            print("processing batch")
            condition_str = '\n'.join(skin_conditions)
            replacements = do_inference(condition_str)
            combined_replacements.update(replacements)
            skin_conditions = []

    if len(skin_conditions) > 0:
        print("processing last batch")
        condition_str = '\n'.join(skin_conditions)
        replacements = do_inference(condition_str)
        combined_replacements.update(replacements)

    print("combined_replacements:", combined_replacements)

    skin_df = dbt.source("skincare_products_raw", "skin_disease_picture")
        
    output_df = skin_df.na.replace(combined_replacements, "skin_condition_name")
    
    return output_df
