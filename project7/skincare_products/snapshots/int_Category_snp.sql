{% snapshot int_Category_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='category_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Category') }}

{% endsnapshot %}