from django_filters import rest_framework
from rest_framework.generics import ListAPIView

from common.location.models import Country, State, City
from common.location.pagination import LocationResultsSetPagination
from common.location.serializers import CountrySerializer, StateSerializer, CitySerializer
from common.location.constants import COUNTRY_LIST_SUCCESS_MESSAGE, STATE_LIST_SUCCESS_MESSAGE, CITY_LIST_SUCCESS_MESSAGE


from utils.helpers import create_response
from utils.db_interactors import db_get_object_list, get_select_related_object_list


class CountryFilterSet(rest_framework.FilterSet):
    name = rest_framework.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Country
        fields = ('name', )


class CountryListView(ListAPIView):
    """
    View to list the countries

    This endpoint lists all the countries and also provides pagination and filters.
    """
    serializer_class = CountrySerializer
    queryset = db_get_object_list(Country)[1]
    filter_backends = (rest_framework.DjangoFilterBackend, )
    filterset_class = CountryFilterSet
    permission_classes = []
    authentication_classes = []
    
    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        return create_response(success=True, message=COUNTRY_LIST_SUCCESS_MESSAGE, data=res.data)


class StateFilterSet(rest_framework.FilterSet):
    name = rest_framework.CharFilter(field_name='name', lookup_expr='icontains')
    country = rest_framework.CharFilter(field_name='country__name', lookup_expr='icontains')
    country_id = rest_framework.NumberFilter(field_name='country__id', lookup_expr='exact')

    class Meta:
        model = State
        fields = ('name', 'country', 'country_id')


class StateListView(ListAPIView):
    """
    View to list the countries

    This endpoint lists all the countries and also provides pagination and filters.
    """
    serializer_class = StateSerializer
    queryset = get_select_related_object_list(State, foreign_key_fields=['country'])[1]
    filter_backends = (rest_framework.DjangoFilterBackend, )
    filterset_class = StateFilterSet
    pagination_class = LocationResultsSetPagination
    permission_classes = []
    authentication_classes = []

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                filters = self.request.query_params
                if filters != {}:
                    self._paginator = None
                else:
                    self._paginator = self.pagination_class()
        return self._paginator

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        return create_response(success=True, message=STATE_LIST_SUCCESS_MESSAGE, data=res.data)


class CityFilterSet(rest_framework.FilterSet):
    name = rest_framework.CharFilter(field_name='name', lookup_expr='icontains')
    state = rest_framework.CharFilter(field_name='state__name', lookup_expr='icontains')
    state_id = rest_framework.NumberFilter(field_name='state__id', lookup_expr='exact')
    country = rest_framework.CharFilter(field_name='state__country__name', lookup_expr='icontains')
    country_id = rest_framework.NumberFilter(field_name='state__country__id', lookup_expr='exact')

    class Meta:
        model = City
        fields = ('name', 'state')


class CityListView(ListAPIView):
    """
    View to list the countries

    This endpoint lists all the countries and also provides pagination and filters.
    """
    serializer_class = CitySerializer
    queryset = get_select_related_object_list(City, foreign_key_fields=['state__country'])[1]
    filter_backends = (rest_framework.DjangoFilterBackend, )
    filterset_class = CityFilterSet
    pagination_class = LocationResultsSetPagination
    authentication_classes = []
    permission_classes = []
    
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                filters = self.request.query_params
                if filters != {}:
                    self._paginator = None
                else:
                    self._paginator = self.pagination_class()
        return self._paginator

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        return create_response(success=True, message=CITY_LIST_SUCCESS_MESSAGE, data=res.data)

