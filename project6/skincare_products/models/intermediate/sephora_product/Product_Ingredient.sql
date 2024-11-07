WITH int_Product_Ingredient AS (
  SELECT
    sp.product_id, -- Primary key from the sephora_product table
    UPPER(ci.ingredient_unique_name) AS ingredient_unique_name -- Make lowercase
  FROM
    (SELECT
      product_id,
      ingredient -- Split the treatments into individual ingredients
    FROM
      {{ ref('tmp_sephora_product') }},
      UNNEST(ingredients) AS ingredient
    WHERE ARRAY_LENGTH(ingredients) > 0) sp
  JOIN
    {{ ref('Cosmetic_Ingredient') }} ci
  ON
    LOWER(ci.ingredient_unique_name) = LOWER(sp.ingredient) -- Compare in lowercase
)

SELECT *
FROM int_Product_Ingredient
