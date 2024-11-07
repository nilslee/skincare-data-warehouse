with int_Product_Highlight as (
  with product_data as (
      select
          product_id,
          split(replace(replace(feature_highlights, '[', ''), ']', ''), ', ') as feature_highlights_array
      from {{ ref('sephora_product') }}
  ),
  highlight_data as (
      select
          product_id,
          feature_highlight,
          dense_rank() over (order by feature_highlight) as highlight_id
      from product_data,
      unnest(feature_highlights_array) as feature_highlight
  )
  select
      distinct product_id,
      highlight_id
  from highlight_data
)

select *
from int_Product_Highlight