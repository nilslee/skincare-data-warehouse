{% snapshot mrt_out_of_stock_pricing_trends_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='id',
          check_cols=['product_name','price_usd','sale_price_usd','variation_min_price', 'variation_max_price', 'variation_count'],
        )
    }}

    select product_name || '-' || price_usd || '-' || sale_price_usd || '-' || variation_min_price || '-' || variation_max_price || '-' || variation_count as id, * 
	from {{ ref('mrt_out_of_stock_pricing_trends') }}

{% endsnapshot %}