{% snapshot raw_sephora_products_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='product_id',
          updated_at='_load_time',
        )
    }}

    select * 
	    from {{ source('skincare_products_raw', 'sephora_product') }}

{% endsnapshot %}