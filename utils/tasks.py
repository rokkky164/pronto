# tasks.py
from functools import wraps
import inspect
from celery import Task, shared_task
from django.conf import settings
# from prepstudyAPI.middlewares import log_data_to_datadog
from json import dumps
import urllib.parse
import urllib.request


def log_data_to_datadog(log_data: any):
    """
    log data to datadog
    :param log_data: log_data
    :return: success or error
    """

    parameters = {"ddsource": "TradePronto-API"}
    try:
        parse_params = urllib.parse.urlencode(parameters)
        json_data = dumps(log_data)
        data = json_data.encode("utf-8")
        intake_datadog_url = settings.DD_INTAKE_URL
        data_dog_key = settings.DD_API_KEY
        request_url = f"""https://{intake_datadog_url}/v1/input/{data_dog_key}/?{parse_params}"""
        req = urllib.request.Request(request_url, data=data, headers={"content-type": "application/json"})
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"\n*** Error while sending logs to datadog.*** log_data: {log_data}. Error: {str(e)}")


@shared_task
def log_data_to_datadog_task(log_data: any):
    log_data_to_datadog(log_data)


def send_celery_logs_to_dd(
        task_name,
        task_id=None,
        eta=None,
        user_id=None,
        success: bool = False,
        task_status: str = "Processing",
        response=None,
        **kwargs
):
    env = settings.DD_ENVIRONMENT
    if env != 'local':
        kwargs = {
            key: value if type(value) in [list, dict, set, str] else str(value) for key, value in kwargs.items()
        }
        log_data = {
            'task_id': task_id,
            'task_name': task_name,
            'eta': eta,
            'task_status': task_status,
            'params': kwargs,
            'response': response,
            "request_user": str(user_id) if user_id else None,
            "service": "Worker",
            "host": settings.DD_ENVIRONMENT,
            "level": 'INFO' if success else 'ERROR'
        }
        log_data_to_datadog_task.delay(log_data=log_data)


def base_task(task):
    @shared_task
    @wraps(task)
    def wrapper(*args, **kwargs):
        task_id = wrapper.request.id
        # Perform some actions before the task runs, if needed
        result = task(*args, **kwargs)
        # Perform some actions after the task runs, if needed

        env = settings.DD_ENVIRONMENT
        if env != 'local':
            send_celery_logs_to_dd(
                task_id=task_id,
                task_name=task.__name__,
                user_id=kwargs.get('user', kwargs.get('user_id', None)),
                exam_id=kwargs.get('exam', kwargs.get('exam_id', None)),
                success=True if result or result is None else False,
                eta=wrapper.request.eta,
                task_status='Schedule' if wrapper.request.eta else 'Schedule Now'
            )
        return result
    return wrapper
