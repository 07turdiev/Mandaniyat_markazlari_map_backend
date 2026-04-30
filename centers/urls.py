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
    path('slides/', views.slides_list, name='slides-list'),
    path('centers/<int:pk>/passport-pdf/', views.passport_pdf, name='passport-pdf'),
    path('guesthouse/', views.guesthouse_detail, name='guesthouse-detail'),
    path('exemplary-center/', views.exemplary_center_detail, name='exemplary-center-detail'),
    # Admin AJAX endpointlari
    path('ajax/translate/', views.ajax_translate, name='ajax-translate'),
    path('ajax/centers-by-district/<int:district_id>/', views.ajax_centers_by_district, name='ajax-centers-by-district'),
    path('ajax/districts/<int:region_id>/', views.ajax_districts, name='ajax-districts'),
    path('ajax/mahallas/<int:district_id>/', views.ajax_mahallas, name='ajax-mahallas'),
]
