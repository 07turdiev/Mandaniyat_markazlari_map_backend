from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'districts', views.DistrictViewSet)
router.register(r'centers', views.CulturalCenterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('map-data/', views.map_data, name='map-data'),
    path('statistics/', views.statistics, name='statistics'),
]
