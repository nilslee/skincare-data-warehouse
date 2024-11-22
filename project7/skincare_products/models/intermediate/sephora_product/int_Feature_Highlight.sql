{{
    config(
        unique_key='highlight_id'
    )
}}

with int_Feature_Highlight as (
    with product_data as (
        select
            split(replace(replace(feature_highlights, '[', ''), ']', ''), ', ') as feature_highlights_array, _load_time
        from {{ ref('int_tmp_cosine_sephora_ingredients') }}
        where dbt_valid_to is null
    ),
    highlight_data as (
        select
            feature_highlight,
            dense_rank() over (order by feature_highlight) as highlight_id, _load_time
        from product_data,
        unnest(feature_highlights_array) as feature_highlight
    )
    select distinct
        highlight_id,
        feature_highlight,
        _load_time
    from highlight_data
    order by highlight_id
)

select *
from int_Feature_Highlight
where highlight_id not in (select highlight_id from int_Feature_Highlight group by highlight_id having count(*) > 1)

/// DIDNT USE