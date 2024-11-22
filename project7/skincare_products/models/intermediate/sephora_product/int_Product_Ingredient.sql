{{
    config(
        unique_key='product_id'
    )
}}

WITH int_Product_Ingredient AS (
  SELECT
    sp.product_id, -- Primary key from the sephora_product table
    UPPER(ci.ingredient_unique_name) AS ingredient_unique_name,
    sp._load_time -- Ensure _load_time is selected from the source table
  FROM
    (
      SELECT
        product_id,
        ingredient,
        _load_time
      FROM
        {{ ref('int_tmp_sephora_product') }},
        UNNEST(ingredients) AS ingredient
      WHERE ARRAY_LENGTH(ingredients) > 0
    ) sp
  JOIN
    {{ ref('int_Cosmetic_Ingredient') }} ci
  ON
    LOWER(ci.ingredient_unique_name) = LOWER(sp.ingredient) -- Compare in lowercase
)

SELECT *
FROM int_Product_Ingredient
WHERE product_id NOT IN (
    SELECT product_id
    FROM int_Product_Ingredient
    GROUP BY product_id
    HAVING COUNT(*) > 1
)
