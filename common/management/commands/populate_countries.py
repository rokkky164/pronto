import logging
import re
from datetime import datetime
from json import load

from django.core.management import BaseCommand

from common.location.models import City, State, Country
from utils.db_interactors import db_create_record

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate countries, states and cities'

    def add_arguments(self, parser):
        # optional arguments
        parser.add_argument(
            '--dry',
            action='append',
            type=str,
        )

    def handle(self, *args, **kwargs):
        dry = kwargs.get('dry')
        with open("/home/roshan/Downloads/countries+states+cities.json") as file:
            countries = load(file)
            for country in countries:
                country_name = country['name']
                status, country_obj = db_create_record(model=Country, data={'name': country_name})
                for state in country['states']:
                    status, state_obj = db_create_record(model=State, data={'name': state['name'], 'country': country_obj})
                    cities = state['cities']
                    for city in cities:
                        status, city = db_create_record(model=State, data={'city': city['name'], 'state': state_obj})
