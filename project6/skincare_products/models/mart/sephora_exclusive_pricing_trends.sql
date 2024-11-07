with sephora_exclusive_pricing_trends as (
  select
      p.product_name,
      pr.price_usd,
      pr.sale_price_usd,
      pv.variation_min_price,
      pv.variation_max_price,
      pv.variation_count
  from
      {{ ref('Product_Stock_Status') }} ps
  join
      {{ ref('Product_Price') }} pr
      on ps.product_id = pr.product_id
  join
      {{ ref('Product_Variation') }} pv
      on ps.product_id = pv.product_id
  join
      {{ ref('Sephora_Product') }} p
      on ps.product_id = p.product_id
  where
      ps.sephora_exclusive = true
)

select *
from sephora_exclusive_pricing_trends