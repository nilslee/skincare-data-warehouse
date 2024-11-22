{{
    config(
        unique_key='product_id'
    )
}}

with int_Product_Category as (
  WITH product_categories as (
    SELECT product_id, primary_category AS category_name, _load_time
    FROM {{ ref('int_tmp_cosine_sephora_ingredients') }}
    WHERE primary_category IS NOT NULL and dbt_valid_to IS NULL

    UNION ALL

    SELECT product_id, secondary_category, _load_time
    FROM {{ ref('int_tmp_cosine_sephora_ingredients') }}
    WHERE secondary_category IS NOT NULL and dbt_valid_to IS NULL

    UNION ALL

    SELECT product_id, tertiary_category, _load_time
    FROM {{ ref('int_tmp_cosine_sephora_ingredients') }}
    WHERE tertiary_category IS NOT NULL and dbt_valid_to IS NULL
  )

  SELECT
    pc.product_id,
    c.category_id,
    pc._load_time
  FROM
    product_categories pc
  LEFT JOIN
    {{ ref('int_Category') }} c
  ON
    pc.category_name = c.category_name
)

SELECT 
    product_id, 
    category_id, 
    MIN(_load_time) AS _load_time
FROM 
    int_Product_Category
WHERE 
    product_id NOT IN (
        SELECT product_id 
        FROM int_Product_Category 
        GROUP BY product_id 
        HAVING COUNT(*) > 1
    )
GROUP BY 
    product_id, 
    category_id
