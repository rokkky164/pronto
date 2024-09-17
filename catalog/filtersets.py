from django.db.models import Q
from django.utils.timezone import now
from django_filters import FilterSet, MultipleChoiceFilter, RangeFilter, BaseInFilter, IsoDateTimeFromToRangeFilter

from .models import (
    Product, Category, ProductVariant,
    ProductConfig, SupplierProducts,
    Manufacturer, ProductReview,
    ProductRatings, ProductImages,
    ShippingAndOrdering
)

class ProductFilterSet(FilterSet):

    def filter_status(self, queryset, name, value):
        user = self.request.user
        filters = Q(status__in=value)
        if set(value).intersection({Exam.Status.ACTIVE, Exam.Status.ASSIGNED}):
            filters &= Q(valid_to__gte=now())
        elif set(value).intersection({Exam.Status.RESULT_GENERATED, Exam.Status.EVALUATING_RESULT}):
            filters |= Q(valid_to__lte=now())

        if user and (user.is_student() or user.is_external_candidate() or user.is_internal_candidate() or user.is_sme()):
            if set(value).intersection({Exam.Status.ACTIVE, Exam.Status.READY, Exam.Status.ASSIGNED})\
                    and not set(value).intersection({Exam.Status.RESULT_GENERATED, Exam.Status.EVALUATING_RESULT}):
                filters &= (Q(exaninee_exam_map__student=user)
                            & ~Q(exaninee_exam_map__examinee_status=ExamineeExamMap.ExamineeStatus.COMPLETED))
                if set(value).intersection({Exam.Status.READY, Exam.Status.ASSIGNED}):
                    marathons = Marathon.objects.filter(created_by=user)
                    if marathons:
                        m_q = queryset
                        other_exams = list(queryset.filter(~(Q(examination_type=Exam.ExaminationType.MARATHON))).values_list('id', flat=True).distinct())
                        for marathon in marathons:
                            marathon_exams = \
                                m_q.filter(Q(exam_marathon_map__marathon__id=marathon.id) & 
                                    Q(valid_from__gt=now())).order_by('valid_from').values_list('id', flat=True).distinct()[:1]
                            if marathon_exams:
                                other_exams += list(marathon_exams)
                        queryset = Exam.objects.filter(Q(id__in=other_exams))

            elif set(value).intersection({Exam.Status.RESULT_GENERATED, Exam.Status.EVALUATING_RESULT}):
                filters |= (Q(exaninee_exam_map__student=user)
                            & Q(exaninee_exam_map__examinee_status=ExamineeExamMap.ExamineeStatus.COMPLETED))
        return queryset.filter(filters)

    class Meta:
        model = Product
        exclude = ['created', 'updated']

    status = MultipleChoiceFilter(choices=Exam.Status.choices, method='filter_status')
    exam_type = BaseInFilter(field_name='exam_type', lookup_expr='in')
    examination_type = MultipleChoiceFilter(choices=Exam.ExaminationType.choices)
    duration = RangeFilter()
    grade = BaseInFilter(field_name='grade', lookup_expr='in')
    batch = BaseInFilter(field_name='batch_exam_map__batch', lookup_expr='in')
    valid_from = IsoDateTimeFromToRangeFilter()
    valid_to = IsoDateTimeFromToRangeFilter()
    subject = BaseInFilter(field_name='question_paper__question_sets__subject', lookup_expr='in')
    topic = BaseInFilter(field_name='question_paper__question_sets__question_set_questions__topic', lookup_expr='in')
    institute = BaseInFilter(lookup_expr='in')
