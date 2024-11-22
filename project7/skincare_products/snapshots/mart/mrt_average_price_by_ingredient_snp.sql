{% snapshot mrt_average_price_by_ingredient_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='ingredient_unique_name',
          check_cols=['ingredient_unique_name', 'average_price', 'product_count'],
        )
    }}

    select * 
	from {{ ref('mrt_average_price_by_ingredient') }}

{% endsnapshot %}