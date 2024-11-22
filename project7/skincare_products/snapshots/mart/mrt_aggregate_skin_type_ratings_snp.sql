{% snapshot mrt_aggregate_skin_type_ratings_snp %}

    {{
        config(
          target_schema='inc_skincare_products_snp',
          strategy='check',
          unique_key='skin_condition',
          check_cols=['average_rating'],
        )
    }}

    select * 
	from {{ ref('mrt_aggregate_skin_type_ratings') }}

{% endsnapshot %}