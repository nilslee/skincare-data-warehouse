WITH tmp_ingredient_official_names AS (
  SELECT ingredient_unique_name FROM {{ ref('Cosmetic_Ingredient') }}
  WHERE ingredient_unique_name IS NOT NULL
)

SELECT *
FROM tmp_ingredient_official_names