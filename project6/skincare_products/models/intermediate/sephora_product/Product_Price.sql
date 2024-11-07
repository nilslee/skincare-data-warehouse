with int_Product_Price as (
  select
      ROW_NUMBER() OVER () as price_id,
      product_id,
      price_usd,
      value_price_usd,
      sale_price_usd
  from {{ ref('sephora_product') }}
  where price_usd is not null
    or value_price_usd is not null
    or sale_price_usd is not null
)

select *
from int_Product_Price