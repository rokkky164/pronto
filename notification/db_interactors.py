from .models import Notification


def get_notifications(user):
	return Notification.objects.filter(sender=user)
