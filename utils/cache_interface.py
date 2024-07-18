from django.core.cache import cache


def get_value(key: str = None):
    try:
        return True, cache.get(key)
    except Exception as e:
        return False, str(e)


def set_value(key: str = None, value=None, expire_on: int = 2592000):
    # Default expire time is 30 days. cache will be removed after 30 days.
    try:
        return True, cache.set(key, value, expire_on)
    except Exception as e:
        return False, str(e)


def remove_keys(key_list: list = None):
    try:
        return True, cache.delete_many(key_list)
    except Exception as e:
        return False, str(e)
