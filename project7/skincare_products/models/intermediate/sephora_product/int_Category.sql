{{
    config(
        unique_key='category_id'
    )
}}

with int_Category as (
  WITH combined_categories AS (
    SELECT primary_category AS category_name, _load_time
    FROM {{ ref('int_tmp_cosine_sephora_ingredients') }}
    WHERE primary_category IS NOT NULL AND dbt_valid_to IS NULL

    UNION ALL

    SELECT secondary_category AS category_name, _load_time
    FROM {{ ref('int_tmp_cosine_sephora_ingredients') }}
    WHERE secondary_category IS NOT NULL AND dbt_valid_to IS NULL

    UNION ALL

    SELECT tertiary_category AS category_name, _load_time
    FROM {{ ref('int_tmp_cosine_sephora_ingredients') }}
    WHERE tertiary_category IS NOT NULL AND dbt_valid_to IS NULL
)

SELECT
  ROW_NUMBER() OVER () AS category_id,
  category_name,
  MIN(_load_time) AS _load_time
FROM (
  SELECT DISTINCT category_name, _load_time
  FROM combined_categories
)
GROUP BY category_name
)

select *
from int_Category
where category_id not in (select category_id from int_Category group by category_id having count(*) > 1)