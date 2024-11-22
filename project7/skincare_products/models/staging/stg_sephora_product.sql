{{
    config(
        unique_key='product_id'
    )
}}

with stg_sephora_product as (
	select 
    product_id,
    product_name,
    brand_id,
    brand_name,
    loves_count,
    rating,
    reviews,
    case
      when size not like '% oz%'
        and size not like '% g%'
        and size not like '% mL%'
        and size not like '% ml%'
        and size not like '% in%'
        and size not like '% inches%'
        and size not like '% Inches%'
        and size not like '%/%'
      then size
      else null
    end as other_size,
    case
      when contains_substr(size, '/') then split(size, '/')[SAFE_OFFSET(0)]
      when size like '% oz%'
        or size like '% inches%'
        or size like '% Inches%'
      then size
      else null
    end as imperial_size,
    case
      when contains_substr(size, '/') then split(size, '/')[SAFE_OFFSET(1)]
      when size like '% g%'
        or size like '% mL%'
        or size like '% ml%'
      then size
      else null
    end as metric_size,
    case
      when variation_type like '%Color%' then variation_value
      else null
    end as color,
    child_count as variation_count,
    child_max_price as variation_max_price,
    child_min_price as variation_min_price,
    SPLIT(REGEXP_REPLACE(ingredients, r"[\[\]']", ''), ', ') AS ingredients,
    price_usd,
    value_price_usd,
    sale_price_usd,
    safe_cast(limited_edition as BOOLEAN) as limited_edition,
    safe_cast(`new` as BOOLEAN) as new_product,
    safe_cast(online_only as BOOLEAN) as online_only,
    safe_cast(out_of_stock as BOOLEAN) as out_of_stock,
    safe_cast(sephora_exclusive as BOOLEAN) as sephora_exclusive,
    highlights as feature_highlights,
    primary_category,
    secondary_category,
    tertiary_category,
    _data_source,
    _load_time
	from {{ ref('int_tmp_sephora_product_ingrediients') }}
  where dbt_valid_to is null
)

select *
from stg_sephora_product
