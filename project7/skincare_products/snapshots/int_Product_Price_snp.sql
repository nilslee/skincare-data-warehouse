{% snapshot int_Product_Price_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='price_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Product_Price') }}

{% endsnapshot %}