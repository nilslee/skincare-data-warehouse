{% snapshot int_Product_Size_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='size_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Product_Size') }}

{% endsnapshot %}