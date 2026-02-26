from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelProjectViewSet, PlaceViewSet, PlaceSearchAPIView

router = DefaultRouter()
router.register(r'projects', TravelProjectViewSet, basename='project')
router.register(r'places', PlaceViewSet, basename='place')

urlpatterns = [
    path('places/search/', PlaceSearchAPIView.as_view(), name='place-search'),
    path('', include(router.urls)),
]
