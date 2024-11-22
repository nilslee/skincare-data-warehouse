from pyspark.sql.functions import col, when, expr

def model(dbt, session):
    dbt.config(incremental_strategy = "insert_overwrite")
    dbt.config(unique_key = "id")

    # Load the latest temp table
    final_df = dbt.ref("stg_tmp_dermatologic_disease_2_standardized_ingredients")

    # Update 'causes' column, setting it to None if it's "N/A" or "Not applicable"
    final_df = final_df.withColumn("causes", when(col("causes").isin("N/A", "Not applicable"), None).otherwise (col("causes")))
    
    # Drop the 'processed_treatments' column
    final_df = final_df.drop("processed_treatments","dbt_scd_id", "dbt_updated_at", "dbt_valid_from", "dbt_valid_to")

    return final_df


