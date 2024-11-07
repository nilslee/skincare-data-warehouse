with int_Feature_Highlight as (
    with product_data as (
        select
            split(replace(replace(feature_highlights, '[', ''), ']', ''), ', ') as feature_highlights_array
        from {{ ref('sephora_product') }}
    ),
    highlight_data as (
        select
            feature_highlight,
            dense_rank() over (order by feature_highlight) as highlight_id
        from product_data,
        unnest(feature_highlights_array) as feature_highlight
    )
    select distinct
        highlight_id,
        feature_highlight
    from highlight_data
    order by highlight_id
)

select *
from int_Feature_Highlight