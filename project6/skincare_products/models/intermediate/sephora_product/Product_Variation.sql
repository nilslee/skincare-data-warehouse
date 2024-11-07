with int_Product_Variation as (
  select
      ROW_NUMBER() OVER () as variation_id, product_id, variation_count, variation_max_price, variation_min_price
  from {{ ref('sephora_product') }}
  where variation_count is not null
    or variation_max_price is not null
    or variation_min_price is not null
)

select *
from int_Product_Variation