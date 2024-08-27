from django.contrib import admin

from common.location.models import Country, State, City
from utils.admin import CustomBaseModelAdmin


@admin.register(Country)
class CountryAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )
    model = Country
    verbose_name = "Country"


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )
    model = State
    verbose_name = "State"


@admin.register(City)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )
    model = City
    verbose_name = "City"
