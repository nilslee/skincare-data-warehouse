WITH mrt_category_rating as (
  with review_category as (
    select
      c.category_name,
      spr.*
    from
      {{ ref('Sephora_Product_Review') }} spr
    left join {{ ref('Product_Category') }} pc on pc.product_id = spr.product_id
    left join {{ ref('Category') }} c on c.category_id = pc.category_id
  )

  select
    category_name,
    CAST(avg(rating) as FLOAT64) as average_rating,
    count(review_id) as review_count
  from
    review_category
  group by
    category_name
  order by
    review_count desc
)

SELECT *
FROM mrt_category_rating