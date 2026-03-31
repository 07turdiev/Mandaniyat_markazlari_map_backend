from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'districts', views.DistrictViewSet)
router.register(r'mahallas', views.MahallaViewSet)
router.register(r'centers', views.CulturalCenterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('map-data/', views.map_data, name='map-data'),
    path('statistics/', views.statistics, name='statistics'),
    # Admin AJAX endpointlari
    path('ajax/districts/<int:region_id>/', views.ajax_districts, name='ajax-districts'),
    path('ajax/mahallas/<int:district_id>/', views.ajax_mahallas, name='ajax-mahallas'),
]
