from rest_framework import serializers

from common.location.models import Country, State, City


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        exclude = ('country', )


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        exclude = ('state', )

