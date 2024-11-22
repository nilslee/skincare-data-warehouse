{% snapshot mrt_category_rating_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='category_name',
          check_cols=['category_name', 'average_rating', 'review_count'],
        )
    }}

    select * 
	from {{ ref('mrt_category_rating') }}

{% endsnapshot %}