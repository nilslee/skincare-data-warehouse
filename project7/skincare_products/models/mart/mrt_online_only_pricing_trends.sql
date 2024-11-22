{{
    config(
        unique_key='product_id'
    )
}}

with online_only_pricing_trends as (
  select
      p.product_name,
      pr.price_usd,
      pr.sale_price_usd,
      pv.variation_min_price,
      pv.variation_max_price,
      pv.variation_count
  from
      {{ ref('int_Product_Stock_Status_snp') }} ps
  join
      {{ ref('int_Product_Price_snp') }} pr
      on ps.product_id = pr.product_id
  join
      {{ ref('int_Product_Variation_snp') }} pv
      on ps.product_id = pv.product_id
  join
      {{ ref('int_Sephora_Product_snp') }} p
      on ps.product_id = p.product_id
  where
      ps.online_only = true
)

select *
from online_only_pricing_trends