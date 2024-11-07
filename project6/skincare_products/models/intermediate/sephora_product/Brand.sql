with int_Brand as (
    select
        distinct brand_id,
        brand_name
    from {{ ref('sephora_product') }}
)

select *
from int_Brand