{% snapshot mrt_aggregate_stock_status_prices_snp
 %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='stock_status',
          check_cols=['average_price'],
        )
    }}

    select * 
	from {{ ref('mrt_aggregate_stock_status_prices') }}

{% endsnapshot %}