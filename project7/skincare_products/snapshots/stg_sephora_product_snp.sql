{% snapshot stg_sephora_product_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='product_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('stg_sephora_product') }}

{% endsnapshot %}