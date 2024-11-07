from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType

# Function to replace ingredients in each treatment list
def replace_ingredients(treatments, replacements_dict):
  print("original treatments: ", treatments)

  # Check if treatments is NULL or not a list (e.g., None)
  if treatments is None or not isinstance(treatments, list):
    return treatments

  # Check if treatments array is empty
  if len(treatments) == 0:
    return treatments

  standardized_treatments = []

  # Iterate through each ingredient in the treatments array
  treatments = [x.lower() for x in treatments]
  for ingredient in treatments:
    ingredient = ingredient.replace("\"", "")

    # Replace with standardized name if it exists in the replacements dictionary
    standardized_ingredient = replacements_dict.get(ingredient, ingredient)
    standardized_treatments.append(standardized_ingredient.upper())

  print("standardized_treatments: ", standardized_treatments)
  return standardized_treatments


# Define the UDF and integrate broadcasted replacements dictionary
def replace_ingredients_udf(treatments):
  return replace_ingredients(treatments, replacements_broadcast.value)

replace_ingredients_udf = udf(replace_ingredients_udf, ArrayType(StringType()))


def model(dbt, session):
  # Fetch the data from BigQuery into a DataFrame
  df = dbt.ref("tmp_dermatologic_disease")
  replacements_df = dbt.ref("tmp_ingredient_replacements")

  # Convert replacements_df to dictionary. old_ingredient and new_ingredient are columns {"some old_ingredient" : "some new_ingredient", ...}
  replacements = dict(replacements_df.select("old_ingredient", "new_ingredient").rdd.map(lambda row: (row.old_ingredient.lower(), row.new_ingredient.lower())).collect())
  
  # Broadcast the replacements dictionary
  global replacements_broadcast
  replacements_broadcast = session.sparkContext.broadcast(replacements)
  
  # Replace ingredient names
  df = df.withColumn("treatments", replace_ingredients_udf(df["treatments"]))

  return df