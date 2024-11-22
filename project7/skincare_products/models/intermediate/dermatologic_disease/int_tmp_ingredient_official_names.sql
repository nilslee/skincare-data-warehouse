WITH tmp_ingredient_official_names AS (
  SELECT ingredient_unique_name, _load_time FROM {{ ref('int_Cosmetic_Ingredient_snp') }}
  WHERE ingredient_unique_name IS NOT NULL
    AND dbt_valid_to is null
)

SELECT *
FROM tmp_ingredient_official_names