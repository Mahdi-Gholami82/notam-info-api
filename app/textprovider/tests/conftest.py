import pytest
from rest_framework_api_key.models import APIKey
from rest_framework.test import APIClient


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture(scope='function')
def authenticate(api_client : APIClient):
    def do_authenticate(revoked=False):
        key = APIKey.objects.create_key(name='Test',revoked=revoked)[-1]
        api_client.credentials(HTTP_AUTHORIZATION= f'Api-Key {key}')
    return do_authenticate