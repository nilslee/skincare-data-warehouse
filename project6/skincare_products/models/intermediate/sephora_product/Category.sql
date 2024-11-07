with int_Category as (
  WITH combined_categories AS (
    SELECT primary_category AS category_name
    FROM {{ ref('sephora_product') }}
    WHERE primary_category IS NOT NULL

    UNION ALL

    SELECT secondary_category
    FROM {{ ref('sephora_product') }}
    WHERE secondary_category IS NOT NULL

    UNION ALL

    SELECT tertiary_category
    FROM {{ ref('sephora_product') }}
    WHERE tertiary_category IS NOT NULL
  )
  SELECT
    ROW_NUMBER() OVER () AS category_id,
    category_name
  FROM (
    SELECT DISTINCT category_name
    FROM combined_categories
  )
)

select *
from int_Category