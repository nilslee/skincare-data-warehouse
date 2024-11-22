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
    dbt.config(incremental_strategy = "insert_overwrite")
    dbt.config(unique_key = "id")

    # Load the data
    rows = dbt.ref('raw_dermatologic_disease_snp')

    # use the is_incremental macro to detect if this is the first run (i.e. we're creating the table)
    # or a subsequent run (i.e. we're upserting into the existing table)
    if dbt.is_incremental:
        print("is_incremental is true")
        max_from_this = f"select max(_load_time) from {dbt.this}"
        rows = rows.filter(rows._load_time >= session.sql(max_from_this).collect()[0][0])
    else:
        print("is_incremental is false")

    # apply UDF to process treatments
    rows = rows.withColumn("treatments", process_treatment_udf("treatments"))

    # Return the processed PySpark DataFrame
    return rows