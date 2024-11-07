with int_Product_Stock_Status as (
  select
      ROW_NUMBER() OVER () as stock_status_id, product_id, limited_edition, new_product, online_only, out_of_stock, sephora_exclusive
  from {{ ref('sephora_product') }}
  where limited_edition is not null
    or new_product is not null
    or online_only is not null
    or out_of_stock is not null
    or sephora_exclusive is not null
)

select *
from int_Product_Stock_Status