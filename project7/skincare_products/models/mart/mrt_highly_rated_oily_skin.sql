{{
    config(
        unique_key='product_name'
    )
}}

with highly_rated_oily_skin as (
  select
      p.product_name,
      avg(r.rating) as average_rating,
      sum(pr.review_count) as total_reviews
  from
      {{ ref('int_Sephora_Product_Review_snp') }} r
  join
      {{ ref('int_Sephora_Product_snp') }} p
      on r.product_id = p.product_id
  join
      (select
          product_id,
          count(*) as review_count
      from
          {{ ref('int_Sephora_Product_Review_snp') }}
      group by
          product_id) pr
      on p.product_id = pr.product_id
  where
      r.skin_type = 'oily'
  group by
      p.product_name
  order by
      average_rating desc
)

select *
from highly_rated_oily_skin