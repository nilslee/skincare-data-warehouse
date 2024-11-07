import json
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# Define the treatment processing function
def process_treatment(treatment):
    project_id = "segfault-434120"
    region = "us-central1"
    model_name = "gemini-1.5-flash-001"

    prompt = """Go through this treatment string and look for ingredient-based treatments only.
    Format the results as JSON with the schema: original_treatments:string, ingredient_treatments:array<string>."""

    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(model_name)

    try:
        resp = model.generate_content([treatment, prompt], safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            })
        resp_text = resp.text.replace("```json", "").replace("```", "").replace("\n", "")
        result = json.loads(resp_text)
        return json.dumps(result["ingredient_treatments"])
    except:
        return json.dumps([])

# Register the process_treatment function as a UDF
process_treatment_udf = udf(process_treatment, StringType())

def model(dbt, session):
    # Load the data and apply UDF to process treatments
    rows = dbt.source("skincare_products_raw", "dermatologic_disease")
    rows = rows.withColumn("treatments", process_treatment_udf("treatments"))

    # Return the processed PySpark DataFrame
    return rows