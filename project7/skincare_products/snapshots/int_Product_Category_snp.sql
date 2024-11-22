{% snapshot int_Product_Category_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='product_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Product_Category') }}

{% endsnapshot %}