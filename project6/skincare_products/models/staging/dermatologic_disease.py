from pyspark.sql.functions import col, when, expr

def model(dbt, session):
  # Load the latest temp table
  final_df = dbt.ref("tmp_dermatologic_disease_2_standardized_ingredients")

  # Update 'causes' column, setting it to None if it's "N/A" or "Not applicable"
  final_df = final_df.withColumn("causes", when(col("causes").isin("N/A", "Not applicable"), None).otherwise (col("causes")))
  
  # Drop the 'processed_treatments' column
  final_df = final_df.drop("processed_treatments")

  return final_df
