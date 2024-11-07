with stg_sephora_product_review as (
  select
    safe_cast(author_id as INTEGER) as author_id,
    rating,
    CASE
      WHEN is_recommended = 1 THEN TRUE
      WHEN is_recommended = 0 THEN FALSE
      ELSE NULL
    END as is_recommended,
    helpfulness,
    total_feedback_count as review_feedback_count,
    total_pos_feedback_count as review_upvote_count,
    total_neg_feedback_count as review_downvote_count,
    submission_time,
    review_text,
    review_title,
    skin_tone,
    case eye_color when 'Grey' then 'gray' else eye_color end as new_eye_color,
    skin_type,
    hair_color,
    product_id,
    product_name,
    brand_name,
    price_usd,
    _data_source,
    _load_time,
  from {{ source('skincare_products_raw', 'sephora_product_review')}}
)

select *
from stg_sephora_product_review