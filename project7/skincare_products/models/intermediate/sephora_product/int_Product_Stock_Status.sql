{{
    config(
        unique_key='stock_status_id'
    )
}}

with int_Product_Stock_Status as (
  select
      ROW_NUMBER() OVER () as stock_status_id, product_id, limited_edition, new_product, online_only, out_of_stock, sephora_exclusive, _load_time
  from {{ ref('int_tmp_cosine_sephora_ingredients') }}
  where limited_edition is not null
    or new_product is not null
    or online_only is not null
    or out_of_stock is not null
    or sephora_exclusive is not null
    and dbt_valid_to is null
)

select *
from int_Product_Stock_Status
where stock_status_id not in (select stock_status_id from int_Product_Stock_Status group by stock_status_id having count(*) > 1)