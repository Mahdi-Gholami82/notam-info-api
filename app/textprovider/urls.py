from rest_framework_nested import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register('notams',views.NotamsViewSet,basename='notams')


urlpatterns = [
    path(r'', include(router.urls)),
]