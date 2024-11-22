#!/bin/sh

# creates the dbt snapshot and model tables in the right sequence, 
# assumes that the raw tables have already been loaded

# cosmetic_ingredient
dbt snapshot --select raw_cosmetic_ingredient_snp
dbt run --select stg_cosmetic_ingredient
dbt snapshot --select stg_cosmetic_ingredient_snp
dbt run --select models/intermediate/cosmetic_ingredient/*
dbt snapshot --select int_Cosmetic_Ingredient_snp

# dermatologic_disease
dbt snapshot --select raw_dermatologic_disease_snp
dbt run --select models/staging/stg_tmp_dermatologic_disease_1_processed_treatments.py   
dbt run --select models/staging/stg_tmp_dermatologic_disease_2_standardized_ingredients.py   
dbt run --select models/staging/stg_dermatologic_disease.py
dbt snapshot --select stg_dermatologic_disease_snp
dbt run --select models/intermediate/dermatologic_disease/int_tmp_dermatologic_disease.sql
dbt run --select models/intermediate/dermatologic_disease/int_tmp_treatment_ingredient_unofficial_names.sql
dbt run --select models/intermediate/dermatologic_disease/int_tmp_ingredient_official_names.sql
dbt run --select models/intermediate/dermatologic_disease/int_tmp_ingredient_replacements.py
dbt run --select models/intermediate/dermatologic_disease/int_Dermatologic_Disease.py
dbt snapshot --select int_Dermatologic_Disease_snp
dbt run --select models/intermediate/disease_ingredient_treatment/int_Disease_Ingredient_Treatment.sql
dbt snapshot --select int_Disease_Ingredient_Treatment_snp

# sephora_product
dbt snapshot --select raw_sephora_product_snp
dbt run --select stg_sephora_product
dbt snapshot --select stg_sephora_product_snp
dbt run --select models/intermediate/sephora_product/*
dbt run --select int_Sephora_Product
dbt snapshot --select int_Sephora_Product_snp

# sephora_product_review
dbt snapshot --select raw_sephora_product_review_snp
dbt run --select stg_sephora_product_review
dbt snapshot --select stg_sephora_product_review_snp
dbt run --select models/intermediate/sephora_product_review/*
dbt run --select int_Sephora_Product_Review
dbt snapshot --select int_Sephora_Product_Review_snp

# marts
dbt run --select models/mart/*
dbt snapshot --select snapshots/mart/*