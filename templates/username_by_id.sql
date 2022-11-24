{% macro username_by_id(entity_table, user_id) %}
select
    user.username
    from {{ entity_table }}
    where user.id={{ user_id }}
{% endmacro %}