from rest_framework.permissions import BasePermission
from accounts.constants import YOU_ARE_NOT_ALLOWED_TO_ACCESS_SCHOOL, YOU_ARE_NOT_ALLOWED_TO_CHANGE_EMAIL
from utils.constants import  YOU_ARE_NOT_ALLOWED_TO_PERFORM_THIS_ACTION


class IsActive(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


class UserPermission(BasePermission):

    message = YOU_ARE_NOT_ALLOWED_TO_PERFORM_THIS_ACTION

    def has_permission(self, request, view):
        if view.action == 'list':
            if not request.user.is_student():
                return True
        elif view.action == 'avatar_list':
            if request.user.is_student():
                return True
        elif view.action == 'retrieve':
            return request.user.id == int(view.kwargs['pk']) or request.user.is_institute_admin() or \
                   request.user.is_prepstudy_admin() or request.user.is_superuser
        elif view.action in ['update', 'student_grades', 'user_exam_types']:
            return True
        elif view.action == 'student_play_profile':
            if request.user.is_student() and hasattr(request.user, 'student_profile'):
                return True
        elif view.action == 'student_dropdown_list':
            if request.user.is_authenticated or request.user.is_active:
                return True
            return False
        elif view.action == 'user_by_email':
            if request.user.is_teacher() or request.user.is_admin() or request.user.is_institute_admin() \
                    or request.user.is_corporate_admin() or request.user.is_prepstudy_admin():
                return True
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_prep_study_admin():
            return True

        if view.action == 'update':
            if request.user.id == obj.id:
                return True

            user_institute = request.user.institute()
            if (request.user.is_institute_admin() or request.user.is_corporate_admin() or request.user.is_branch_admin()
                    or request.user.is_hr_head()) and user_institute and user_institute in request.user.get_branches():
                return True

        return False


class CanChangeEmail(BasePermission):
    message = YOU_ARE_NOT_ALLOWED_TO_CHANGE_EMAIL

    def has_object_permission(self, request, view, obj):
        if view.action == 'change_email':
            return obj.id == int(view.kwargs['pk'])
