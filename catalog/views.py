import logging
from collections import OrderedDict

from django.db.models import Q
from django.db.transaction import atomic, set_rollback
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from utils.helpers import create_response, load_request_json_data, get_hostname_from_request
from utils.db_interactors import get_record_by_filters, get_record_by_id, get_single_record_by_filters, \
    get_select_related_object_list
from .constants import (
    ANSWER_SUBMISSION_SUCCESS,
    EXAM_CREATE_SUCCESS
)
from .filtersets import ExamFilterSet, ExamCreationRequestFilterSet
from .models import (
    Product, Category, ProductVariant,
    ProductConfig, SupplierProducts,
    Manufacturer, ProductReview,
    ProductRatings, ProductImages,
    ShippingAndOrdering
)
from utils.paginations import StandardResultsSetPagination
from .permissions import ProductPermission
from .serializers import (
	ProductCreateSerializer, ProductListSerializer, ManufacturerSerializer,
	ProductReviewSerializer
)
from .tasks import create_product

LOGGER = logging.getLogger(__name__)


class ProductViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin):
    permission_classes = [ProductPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ExamFilterSet
    ordering_fields = ['name', 'valid_to', 'duration', 'valid_from', 'created_at', 'updated_at']
    ordering = ['valid_to']
    search_fields = ['name']

    def get_object(self, *args, **kwargs):
        if self.action == 'batches_by_exam':
            return db_get_exam_for_batch(_id=self.kwargs.get('pk'))
        if self.action == 'payment_details':
            return db_get_exam_for_payment_details(_id=self.kwargs.get('pk'))
        elif self.action == 'generate_student_result':
            return get_record_by_filters(
                model=UserExamSubmissionDetails,
                filters={'exam': self.kwargs.get('pk'), 'user': self.request.data.get('user')},
                distinct=True
            )
        if self.action == 'publish_evaluated_exam':
            status, exam = get_single_record_by_filters(
                model=Exam, filters={'id': self.kwargs.get('pk'), 'evaluation_status': Exam.EvaluationStatus.PENDING})
        else:
            status, exam = db_get_not_deleted_exam_by_id(_id=self.kwargs.get('pk'))
        if not status:
            return False, EXAM_NOT_EXIST_ERROR

        self.check_object_permissions(request=self.request, obj=exam)
        return True, exam

    def get_queryset(self, validated_data=None, exam=None):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()

        if self.action == 'list':
            return db_get_all_exam_for_user(
                user=self.request.user, exclude_examination=self.request.GET.getlist('exclude_examination', []),
                self_own=self.request.GET.get('self_own', False))
        elif self.action == 'mock_exam':
            return get_record_by_filters(model=Exam, filters=(
                    Q(examination_type=Exam.ExaminationType.MOCK) & ~Q(status=Exam.Status.DELETED)), Q_filtering=True,
                                         distinct=True)
        elif self.action == 'nation_wide_exam':
            return db_get_nation_wide_exams(user=self.request.user, categorie=self.request.GET.get('categorie'))

        elif self.action == 'exam_list_evaluation':
            return db_get_exam_list_for_evaluation(user=self.request.user)
        elif self.action == 'exam_count':
            return db_get_exam_count(user=self.request.user)
        elif self.action == 'completed_exam_list':
            return db_get_completed_exam_for_user(
                user=self.request.user, exclude_examination=self.request.GET.getlist('exclude_examination', []))
        elif self.action == 'exam_list_calendar':
            return db_get_exam_list_for_calender(user=self.request.user)
        elif self.action == 'exam_users_list':
            return get_select_related_object_list(model=ExamineeExamMap, filters={'exam': self.kwargs.get('pk')},
                                                foreign_key_fields=['exam','student'])
        elif self.action == 'batches_by_exam':
            return db_get_batches_by_exam(exam=exam)

    def filter_queryset(self, queryset=None):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListShortSerializer
        elif self.action == 'retrieve':
            return ProductDetailsSerializer
        elif self.action == 'update':
            return ProductUpdateSerializer

    @atomic()
    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        data = load_request_json_data(
            request_data=request.data,
            json_key_list=[
            ]
        )

        serializer = serializer_class(data=data, context=self.get_serializer_context())
        if not serializer.is_valid():
            set_rollback(True)
            return create_response(message=serializer.errors)

            if not serializer.is_valid():
                set_rollback(True)
                return create_response(message=serializer.errors)

        validated_data['question_set_data_serialized'] = data.get('question_set_data')
        validated_data['topic_ids'] = data.get('topics', [])
        validated_data['selected_questions'] = data.get('selected_questions', [])

        status, response = exam_serializer.create(validated_data)
        if not status:
            set_rollback(True)
            return create_response(message=response)
        return create_response(message=EXAM_CREATE_SUCCESS, success=True, data={'exam': response})

    def list(self, request, *args, **kwargs):
        page = request.GET.get('page')
        status, queryset = self.get_queryset()
        if not status:
            return create_response(message=exam_queryset)
        queryset = self.filter_queryset(queryset=exam_queryset)
        queryset = list(OrderedDict.fromkeys(exam_queryset))
        if page:
            exam_queryset = self.paginate_queryset(exam_queryset)
        serializer = self.get_serializer(exam_queryset, many=True, context={
                        'attempt_status': request.GET.get('attempt_status'), 'request': self.request, 
                        'get_subjects': request.GET.get('get_subjects')})
        if page:
            serializer = self.get_paginated_response(serializer.data)
        return create_response(success=True, message=LIST_EXAM_SUCCESS, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        status, exam = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=exam)
        serializer_class = self.get_serializer_class()
        return create_response(success=True, message=EXAM_DETAILS_FETCH_SUCCESS,
                                    data=serializer_class(exam, context=self.get_serializer_context()).data)

    @atomic()
    def update(self, request, *args, **kwargs):
        status, exam = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=exam)
        data = load_request_json_data(
            request_data=request.data,
            json_key_list=[
                'question_set_data',
                'difficulty_distribution',
                'reasoning_type_distribution',
            ]
        )
        data['exam'] = exam.id

        serializer = self.get_serializer(data=data, context=self.get_serializer_context())

        if serializer.is_valid():
            # update exam
            status, response = serializer.update(instance=exam, validated_data=serializer.validated_data)
            if not status:
                set_rollback(True)
                return create_response(message=response)

            return create_response(success=True, message=EXAM_UPDATE_SUCCESS)
        else:
            set_rollback(True)
            return create_response(message=serializer.errors)

    @atomic()
    def destroy(self, request, *args, **kwargs):
        status, exam = self.get_object(*args, **kwargs)
        if not status:
            set_rollback(True)
            return create_response(message=exam)

        status, delete_exam = delete_exam_service(exam=exam, user=request.user)
        if not status:
            set_rollback(True)
            return create_response(message=delete_exam)

        return create_response(success=True, message=DELETE_EXAM_SUCCESS)


class ExamCreationRequestViewSet(ModelViewSet):
    permission_classes = [ExamCreationRequestPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ExamCreationRequestFilterSet
    ordering_fields = ['id', 'exam__name', 'due_date']
    ordering = ['-due_date']
    search_fields = ['exam__name']

    def get_object(self):
        return get_record_by_id(model=ExamCreationRequest, _id=self.kwargs.get('pk'))

    def get_queryset(self, validated_data=None):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
        elif self.action == 'list':
            return db_get_exam_assign_requests(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ExamCreationRequestSerializer

    def list(self, request, *args, **kwargs):
        page = request.GET.get('page')
        status, exam_assign_queryset = self.get_queryset()
        if not status:
            return create_response(message=exam_assign_queryset)
        exam_assign_queryset = self.filter_queryset(queryset=exam_assign_queryset)
        if page:
            exam_assign_queryset = self.paginate_queryset(exam_assign_queryset)
        serializer = self.get_serializer(exam_assign_queryset, many=True)
        if page:
            serializer = self.get_paginated_response(serializer.data)
        return create_response(success=True, message=LIST_EXAM_ASSIGN_REQUEST_SUCCESS, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        status, obj = self.get_object()
        if not status:
            return create_response(message=CREATION_REQUEST_DOES_NOT_EXIST)
        return create_response(
            success=True, message=CREATION_REQUEST_FETCH_SUCCESS, data=ExamCreationRequestDetailSerializer(obj).data)


class ExamV2ViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin):
    permission_classes = [ExamPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['name', 'valid_to', 'duration', 'valid_from', 'created_at', 'updated_at']
    ordering = ['valid_to']
    search_fields = ['name']

    def get_object(self, *args, **kwargs):
        if self.action in ['question_paper_by_exam', 'question_by_exam']:
            status, exam = db_get_exam_for_qp(_id=self.kwargs.get('pk'))
            if not status:
                return False, exam
            if not exam:
                return False, EXAM_NOT_EXIST_ERROR
            self.check_object_permissions(request=self.request, obj=exam)
            return True, exam
        status, exam = db_get_exam_v2(_id=self.kwargs.get('pk'))
        if not status:
            return False, exam
        if not exam:
            return False, EXAM_NOT_EXIST_ERROR
        self.check_object_permissions(request=self.request, obj=exam)
        return True, exam

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExamRetrieveV2Serializer

        elif self.action == 'question_paper_by_exam':
            return ExamQuestionPaperSerializer

        elif self.action == 'question_by_exam':
            return ExamQuestionSerializer

    def get_queryset(self, exam=None):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
        elif self.action == 'question_paper_by_exam':
            return db_get_question_paper_by_exam(_id=exam.question_paper.id)
        elif self.action == 'question_by_exam':
            return db_get_question_by_exam(exam=exam,
                                            question_sets=exam.question_paper.question_sets.all())

    def retrieve(self, request, *args, **kwargs):
        status, exam = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=exam)
        serializer_class = self.get_serializer_class()
        serializer =serializer_class(exam, context=self.get_serializer_context())
        return create_response(success=True, message=EXAM_DETAILS_FETCH_SUCCESS, data=serializer.data)


    @action(detail=True, methods=['get'], url_name=QUESTION_PAPER_BY_EXAM_URL_NAME, url_path=QUESTION_PAPER_BY_EXAM_URL)
    def question_paper_by_exam(self, request, *args, **kwargs):
        status, exam = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=exam)
        status, question_papar = self.get_queryset(exam=exam)
        if not status:
            return create_response(message=question_papar)
        if not question_papar:
            return create_response(success=True, message=QUESTION_PAPAER_BY_EXAM, data=[])
        serializer_class = self.get_serializer_class()
        serializer =serializer_class(question_papar, context={'exam': exam})
        if not status:
            return create_response(message=question_papar)
        return create_response(success=True, message=QUESTION_PAPAER_BY_EXAM, data=serializer.data)


    @action(detail=True, methods=['get'], url_name=QUESTION_BY_EXAM_URL, url_path=QUESTION_BY_EXAM_URL_NAME)
    def question_by_exam(self, request, *args, **kwargs):
        status, exam = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=exam)
        status, queryset = self.get_queryset(exam=exam)
        if not status:
            return create_response(message=queryset)
        if not queryset:
            return create_response(success=True, message=QUESTION_BY_EXAM, data=[])
        serializer = self.get_serializer(queryset, many=True)
        if not status:
            return create_response(message=queryset)
        return create_response(success=True, message=QUESTION_BY_EXAM, data=serializer.data)
