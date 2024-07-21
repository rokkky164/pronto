from typing import Optional

from django.db.models import QuerySet

"""
Get interactors start.
"""


def db_get_empty_queryset(model=None):
    try:
        return True, model.objects.none()
    except Exception as e:
        return False, str(e)


def db_get_object_list(model):
    try:
        return True, model.objects.all()
    except Exception as e:
        return False, str(e)


def db_get_select_related_single_object(model=None, _id=None, select_related=None):
    try:
        return True, model.objects.select_related(select_related).get(id=_id)
    except model.DoesNotExist:
        return True, None
    except Exception as e:
        return False, str(e)


def get_select_related_object_list(
        model=None, foreign_key_fields: list = None, filters: dict = None, distinct: bool = False,
        q_filter: bool = False):
    try:
        if filters:
            if q_filter:
                if distinct:
                    return True, model.objects.filter(filters).distinct().select_related(*foreign_key_fields)
                return True, model.objects.filter(filters).select_related(*foreign_key_fields)
            if distinct:
                return True, model.objects.filter(**filters).distinct().select_related(*foreign_key_fields)
            return True, model.objects.filter(**filters).select_related(*foreign_key_fields)
        return True, model.objects.select_related(*foreign_key_fields)
    except Exception as e:
        return False, str(e)


def db_get_record_with_prefetch(
        model,
        prefetch_list: list,
        distinct: bool = False,
        filters: dict = None,
        q_filtering: bool = False,
        count: int = None,
        order_by: str = 'id',
) -> tuple[bool, any]:
    try:
        if q_filtering:
            if distinct:
                return True, model.objects.filter(filters).distinct().prefetch_related(*prefetch_list).order_by(order_by)[:count]
            return True, model.objects.filter(filters).prefetch_related(*prefetch_list).order_by(order_by)[:count]
        if filters:
            if distinct:
                return True, model.objects.filter(**filters).distinct().prefetch_related(*prefetch_list).order_by(order_by)[:count]
            return True, model.objects.filter(**filters).prefetch_related(*prefetch_list).order_by(order_by)[:count]
        return True, model.objects.all().prefetch_related(*prefetch_list).order_by(order_by)[:count]
    except Exception as e:
        return False, str(e)


def get_record_by_id(model=None, _id=None):
    try:
        return True, model.objects.get(id=_id)
    except Exception as e:
        return False, str(e)


def db_get_descendants(instance=None, include_self=False):
    try:
        return True, instance.get_descendants(include_self=include_self)
    except Exception as e:
        return False, str(e)


def db_get_family(instance=None):
    try:
        return True, instance.get_family()
    except Exception as e:
        return False, str(e)

def db_get_children(instance=None):
    try:
        return True, instance.get_children()
    except Exception as e:
        return False, str(e)


def get_record_by_filters(
        model=None,
        Q_filtering: bool = False,
        filters: any = None,
        count: int = None,
        order_by: str = 'id',
        distinct: bool = False
) -> tuple[bool, any]:
    try:
        if Q_filtering:
            if distinct:
                return True, model.objects.filter(filters).distinct().order_by(order_by)[:count]
            return True, model.objects.filter(filters).order_by(order_by)[:count]
        if distinct:
            return True, model.objects.filter(**filters).distinct().order_by(order_by)[:count]
        return True, model.objects.filter(**filters).order_by(order_by)[:count]
    except Exception as e:
        return False, str(e)


def get_record_by_filters_using_only(
        model=None,
        Q_filtering: bool = False,
        filters: any = None,
        field_list: list = None,
        order_by: str = 'id',
        select_related_fields: list = None
) -> tuple[bool, any]:
    try:
        if Q_filtering:
            if select_related_fields:
                return (True, model.objects.filter(filters).only(*field_list)
                        .select_related(*select_related_fields).distinct())
            return True, model.objects.filter(filters).only(*field_list).distinct()
        if select_related_fields:
            return (True, model.objects.filter(**filters).only(*field_list)
                    .select_related(*select_related_fields).distinct())
        return True, model.objects.filter(**filters).only(*field_list).order_by(order_by).distinct()
    except Exception as e:
        return False, str(e)


def db_get_value_list_by_filters(
        model=None,
        field_name: str = None,
        filters: any = None,
        flat: bool = True,
        q_filtering: bool = False,
        order_by: str = 'id'
):
    try:
        if filters:
            if q_filtering:
                return \
                    True, model.objects.filter(filters).order_by(order_by).values_list(field_name, flat=flat).distinct()
            return \
                True, model.objects.filter(**filters).order_by(order_by).values_list(field_name, flat=flat).distinct()
        return True, model.objects.all().order_by(order_by).values_list(field_name, flat=flat).distinct()
    except Exception as e:
        return False, str(e)


def db_get_value_list_from_queryset(
        queryset: QuerySet = None,
        field_name: str = None,
        filters: dict = None,
        flat: bool = True,
        q_filtering: bool = False,
        distinct: bool = False,
):
    try:
        if filters:
            if q_filtering:
                if distinct:
                    return True, queryset.filter(filters).values_list(field_name, flat=flat).distinct()
                return True, queryset.filter(filters).values_list(field_name, flat=flat)
            if distinct:
                return True, queryset.filter(**filters).values_list(field_name, flat=flat).distinct()
            return True, queryset.filter(**filters).values_list(field_name, flat=flat)
        if distinct:
            return True, queryset.all().values_list(field_name, flat=flat).distinct()
        return True, queryset.all().values_list(field_name, flat=flat)
    except Exception as e:
        return False, str(e)


def get_single_record_by_filters(model=None, filters: any = None, q_filtering: bool = False) -> tuple:
    try:
        if q_filtering:
            return True, model.objects.get(filters)
        return True, model.objects.get(**filters)
    except Exception as e:
        return False, str(e)


def db_filter_query_set(
        query_set: QuerySet, filters: Optional = None, q_filtering: bool = False, distinct: bool = False
) -> tuple:
    try:
        if not filters:
            if distinct:
                return True, query_set.all().distinct()
            return True, query_set.all()
        elif q_filtering:
            if distinct:
                return True, query_set.filter(filters).distinct()
            return True, query_set.filter(filters)
        if distinct:
            return True, query_set.filter(**filters).distinct()
        return True, query_set.filter(**filters)
    except Exception as e:
        return False, str(e)


def db_check_existing_record(model=None, filters: dict = None, q_filtering: bool = False) -> tuple:
    try:
        if q_filtering:
            return True, model.objects.filter(filters).exists()
        return True, model.objects.filter(**filters).exists()
    except Exception as e:
        return False, str(e)


def db_check_existing_record_for_queryset(queryset=None, filters: dict = None, q_filtering: bool = False) -> tuple:
    try:
        if q_filtering:
            return True, queryset.filter(filters).exists()
        return True, queryset.filter(**filters).exists()
    except Exception as e:
        return False, str(e)


def db_get_record_count_by_filters(model, filters=None, q_filters=None):
    try:
        if q_filters:
            return True, model.objects.filter(q_filters).distinct().count()
        return True, model.objects.filter(**filters).distinct().count()
    except Exception as e:
        return False, str(e)


"""
Get interactors end.
"""

"""
Create interactors start.
"""


def db_create_record(model=None, data: dict = None):
    try:
        return True, model.objects.create(**data)
    except Exception as e:
        return False, str(e)
    

def db_add_many_to_many_field_data(instance=None, field=None, _id_list=None, set_new: bool = False):
    try:
        if set_new:
            getattr(instance, field).set(_id_list)
        else:
            getattr(instance, field).add(*_id_list)
        return True, None
    except Exception as e:
        return False, str(e)


def db_bulk_create(model=None, data_list: list = None):
    try:
        return True, model.objects.bulk_create([model(**record) for record in data_list])
    except Exception as e:
        return False, str(e)


def db_bulk_create_by_obj_list(model=None, obj_list=None):
    try:
        return True, model.objects.bulk_create(obj_list)
    except Exception as e:
        return False, str(e)


"""
Create interactors end.
"""

"""
Update interactors start.
"""


def db_update_record_by_id(model=None, _id: int = None, data: dict = None):
    try:
        return True, model.objects.filter(id=_id).update(**data)
    except Exception as e:
        return False, str(e)


def db_update_instance(instance=None, data: dict = None, foreign_key_data: dict = None) -> tuple:
    try:
        if data:
            instance.__dict__.update(**data)
        if foreign_key_data:
            for foreign_key in foreign_key_data:
                setattr(instance, foreign_key, foreign_key_data[foreign_key])
        instance.save()
        return True, instance
    except Exception as e:
        return False, str(e)


def db_update_queryset(queryset=None, data: dict = None):
    try:
        queryset.update(**data)
        return True, queryset
    except Exception as e:
        return False, str(e)


def db_update_records_with_filters(model=None, filters: dict = None, data: dict = None):
    try:
        return True, model.objects.filter(**filters).update(**data)
    except Exception as e:
        return False, str(e)


"""
Update interactors end.
"""

"""
Delete interactors start.
"""


def db_delete_record_by_id(model=None, _id: int = None):
    try:
        return True, model.objects.filter(id=_id).delete()
    except Exception as e:
        return False, str(e)


def db_delete_many_to_many_fields_data(instance=None, field: str = None, _id_list: list = None):
    try:
        getattr(instance, field).remove(*_id_list)
        return True, None
    except Exception as e:
        return False, str(e)


def db_clear_many_to_many_field(instance=None, field: str = None) -> tuple[bool, any]:
    try:
        getattr(instance, field).clear()
        return True, None
    except Exception as e:
        return False, str(e)


def db_delete_records_by_filters(model=None, filters: dict = None):
    try:
        return True, model.objects.filter(**filters).delete()
    except Exception as e:
        return False, str(e)
    

def db_delete_filter_query_set(
        query_set: QuerySet, filters: Optional = None, q_filtering: bool = False
) -> tuple:
    try:
        if not filters:
            return True, query_set.all().delete()
        elif q_filtering:
            return True, query_set.filter(filters).delete()
        return True, query_set.filter(**filters).delete()
    except Exception as e:
        return False, str(e)


"""
Delete interactors end.
"""
