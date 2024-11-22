{{
    config(
        unique_key='product_id'
    )
}}

with int_Product_Highlight as (
  with product_data as (
      select
          product_id,
          split(replace(replace(feature_highlights, '[', ''), ']', ''), ', ') as feature_highlights_array, _load_time
      from {{ ref('int_tmp_cosine_sephora_ingredients') }}
      where dbt_valid_to is null

  ),
  highlight_data as (
      select
          product_id,
          feature_highlight,
          dense_rank() over (order by feature_highlight) as highlight_id, _load_time
      from product_data,
      unnest(feature_highlights_array) as feature_highlight
  )
  select
      distinct product_id,
      highlight_id, _load_time
  from highlight_data
)

select *
from int_Product_Highlight
where product_id not in (select product_id from int_Product_Highlight group by product_id having count(*) > 1)

/// DIDNT USE