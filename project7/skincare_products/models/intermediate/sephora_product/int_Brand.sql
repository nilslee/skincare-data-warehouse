{{
    config(
        unique_key='brand_id'
    )
}}

with int_Brand as (
    select
        distinct brand_id,
        brand_name,
        _load_time
    from {{ ref('int_tmp_cosine_sephora_ingredients') }}
    where dbt_valid_to is null
)

select *
from int_Brand
where brand_id not in (select brand_id from int_Brand group by brand_id having count(*) > 1)