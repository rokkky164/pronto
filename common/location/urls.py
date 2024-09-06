from django.urls import path

from common.location.views import CountryListView, StateListView, CityListView

app_name = 'location'

urlpatterns = [
    path('country', CountryListView.as_view(), name='country-list'),
    path('state', StateListView.as_view(), name='state-list'),
    path('city', CityListView.as_view(), name='city-list')
]