import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.local')
django.setup()

from random import choice, randint
from locust import HttpUser, task
from django.urls import reverse
from rest_framework_api_key.models import APIKey

class WebSiteUser(HttpUser):
    NOTAMS_ENDPOINT=reverse('notams-list')
    param_choices = [
            dict(),
            {'coordinates': 'true'},
            {'parsed': 'true'},
            {'parsed': 'true', 'coordinates': 'true'} 
    ]

    def on_start(self):
        self.key_obj, self.key = APIKey.objects.create_key(name='Test')

    def on_stop(self):
        self.key_obj.delete()

    def retrieve_notams(self,params):
        notam_id = randint(1,20)
        self.client.get(
            self.NOTAMS_ENDPOINT + f'{notam_id}/',
            name=self.NOTAMS_ENDPOINT + 'id/',
            headers={"authorization": f'Api-Key {self.key}'},
            params=params
            )

    def list_notams(self,params):
        self.client.get(
            self.NOTAMS_ENDPOINT,
            name=self.NOTAMS_ENDPOINT,
            headers={"authorization": f'Api-Key {self.key}'},
            params=params
            )

    @task
    def retrieve_notams_task(self):
        queryparam = choice(self.param_choices)
        self.retrieve_notams(queryparam)

    @task
    def list_notams_task(self):
        queryparam : dict = choice(self.param_choices).copy()
        queryparam['page'] = randint(1,4)
        self.list_notams(queryparam)
