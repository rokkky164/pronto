"""
Elasticsearch filters function
"""
from typing import List, Tuple, Union

from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections


def elastic_search_get_records(
        document,
        term_filters: dict = None,
        terms_filters: dict = None
) -> tuple[bool, any]:
    try:
        search = document.search()
        if not terms_filters and not term_filters:
            search = search.filter()
        else:
            if term_filters:
                for key, value in term_filters.items():
                    search = search.filter('term', **{key: value})
            if terms_filters:
                for key, value in terms_filters.items():
                    search = search.filter('terms', **{key: value})
        return True, search.to_queryset()
    except Exception as e:
        return False, str(e)


def es_get_records_q_filters(document, q_filters) -> tuple[bool, any]:
    try:
        search = document.search().filter(q_filters)
        return True, search
    except Exception as e:
        return False, str(e)


def es_filter_search_records(search, q_filters) -> tuple[bool, any]:
    try:
        search = search.filter(q_filters)
        return True, search
    except Exception as e:
        return False, str(e)


def es_bulk_create(actions_data: List[dict]) -> Tuple[int, Union[int, dict]]:
    return bulk(connections.get_connection(), actions=actions_data, raise_on_exception=True, stats_only=False)
