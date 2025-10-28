from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
import os
import pytest
from rest_framework_api_key.models import APIKey


@pytest.mark.django_db
class TestNotamsPermissions:
    LIST_URL = reverse('notams-list')

    def test_if_user_has_no_api_key_returns_403(self, api_client, authenticate):
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_has_api_key_returns_200(self, api_client, authenticate):
        authenticate()
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_if_user_has_revoked_api_key_returns_403(self, api_client, authenticate):
        authenticate(revoked=True)
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN