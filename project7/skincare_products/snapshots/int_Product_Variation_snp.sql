{% snapshot int_Product_Variation_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='variation_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Product_Variation') }}

{% endsnapshot %}