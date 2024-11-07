WITH RankedIngredients AS (
    SELECT *,
      ROW_NUMBER() OVER (PARTITION BY ingredient_unique_name ORDER BY LENGTH(intended_use) DESC) as rank
    FROM {{ ref('cosmetic_ingredient') }}
), 

int_Cosmetic_Ingredient as (
  SELECT * EXCEPT(rank, cosing_ref_no, _data_source, _load_time)
  FROM RankedIngredients
  WHERE rank = 1 AND ingredient_unique_name IS NOT NULL
)

SELECT *
FROM int_Cosmetic_Ingredient