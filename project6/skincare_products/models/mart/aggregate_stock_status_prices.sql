with aggregate_stock_status_prices as (
    select
        case
            when ps.limited_edition then 'limited_edition'
            when ps.new_product then 'new_product'
            when ps.online_only then 'online_only'
            when ps.out_of_stock then 'out_of_stock'
            when ps.sephora_exclusive then 'sephora_exclusive'
        end as stock_status,
        avg(pp.price_usd) as average_price
    from
        {{ ref('Product_Stock_Status') }} ps
    join
        {{ ref('Product_Price') }} pp
    on
        ps.product_id = pp.product_id
    where
        ps.limited_edition or
        ps.new_product or
        ps.online_only or
        ps.out_of_stock or
        ps.sephora_exclusive
    group by
        stock_status
    order by
        stock_status
)

select *
from aggregate_stock_status_prices