from accounts.models import User


def db_update_password(instance: User, password: str) -> tuple:
    try:
        instance.set_password(password)
        instance.save()
        return True, instance
    except Exception as e:
        return False, str(e)