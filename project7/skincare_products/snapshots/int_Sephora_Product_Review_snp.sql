{% snapshot int_Sephora_Product_Review_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='timestamp',
          unique_key='review_id',
          updated_at='_load_time',
        )
    }}

    select * 
	from {{ ref('int_Sephora_Product_Review') }}

{% endsnapshot %}