with int_Product_Category as (
  WITH product_categories as (
    SELECT product_id, primary_category AS category_name
    FROM {{ ref('sephora_product') }}
    WHERE primary_category IS NOT NULL

    UNION ALL

    SELECT product_id, secondary_category
    FROM {{ ref('sephora_product') }}
    WHERE secondary_category IS NOT NULL

    UNION ALL

    SELECT product_id, tertiary_category
    FROM {{ ref('sephora_product') }}
    WHERE tertiary_category IS NOT NULL
  )

  SELECT
    pc.product_id,
    c.category_id
  FROM
    product_categories pc
  LEFT JOIN
    {{ ref('Category') }} c
  ON
    pc.category_name = c.category_name
)

select *
from int_Product_Category