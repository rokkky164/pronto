from typing import Optional

from django.db.models import QuerySet
from django.utils import timezone

from accounts.models import User
from authorization.models import Role, AccountVerificationRequest, EmailChangeRequest


def get_all_roles() -> QuerySet[Role]:
    return Role.objects.all()
    

def get_role_by_name(name: str):
    try:
        role = Role.objects.get(is_default=True, name=name)
    except Role.DoesNotExist:
        return None
    return role


def get_verification_code_by_user_id(id: int):
    return AccountVerificationRequest.objects.filter(user_id=id).last()


def create_email_change_request(user: User, new_email: str) -> EmailChangeRequest:
    """
    Method to generate new email change request
    """
    # check if a valid email change request exists and return the same else create a new one
    existing_ecr = EmailChangeRequest.objects.filter(user=user, new_email=new_email).last()
    if existing_ecr and existing_ecr.is_valid:
        return existing_ecr
    else:
        ecr = EmailChangeRequest(
            user=user,
            new_email=new_email,
        )
        ecr.save()
        return ecr


def get_email_change_request_by_verification_code(user: User, verification_code: str) -> Optional[EmailChangeRequest]:
    try:
        ecr = EmailChangeRequest.objects.get(user=user, verification_code=verification_code)
        return ecr
    except EmailChangeRequest.DoesNotExist:
        return None


def complete_email_change_request(email_change_request: EmailChangeRequest) -> None:
    email_change_request.is_email_changed = True
    email_change_request.changed_at = timezone.now()
    email_change_request.save()