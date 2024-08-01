from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, MethodNotAllowed, PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken


def custom_exception_handler(exc, context):
	response = {
		'status': 'ERROR'
	}
	if isinstance(exc, NotAuthenticated):
		response.update({
			'message': 'You must be authenticated to access this endpoint.',
		})
		return Response(response, status=status.HTTP_401_UNAUTHORIZED)
	if isinstance(exc, InvalidToken):
		response.update({
			'message': exc.default_detail,
			'data': {
				'token_class': exc.detail.get('messages')[0]['token_class'],
				'token_token_type': exc.detail.get('messages')[0]['token_type'],
				'detail': exc.detail['detail']
			}
		})
		return Response(response, status=status.HTTP_401_UNAUTHORIZED)
	if type(exc) == MethodNotAllowed:
		response.update ({
			'message': 'Looks like this method is not allowed.'
		})
		return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

	if type(exc) == PermissionDenied:
		response.update({
			'message': getattr(exc, 'detail', exc.default_detail)
		})
		return Response(response, status=status.HTTP_403_FORBIDDEN)
	# default case
	return exception_handler(exc, context)
