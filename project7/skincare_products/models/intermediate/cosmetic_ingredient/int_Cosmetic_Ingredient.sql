{{
    config(
        unique_key='ingredient_unique_name'
    )
}}

WITH RankedIngredients AS (
    SELECT *,
      ROW_NUMBER() OVER (PARTITION BY ingredient_unique_name ORDER BY LENGTH(intended_use) DESC) as rank
    FROM {{ ref('stg_cosmetic_ingredient_snp') }}
), 

int_Cosmetic_Ingredient as (
  SELECT * EXCEPT(rank, cosing_ref_no, _data_source, dbt_scd_id, dbt_updated_at, dbt_valid_from, dbt_valid_to)
  FROM RankedIngredients
  WHERE rank = 1 
    AND ingredient_unique_name IS NOT NULL
    AND dbt_valid_to is null
)

SELECT *
FROM int_Cosmetic_Ingredient