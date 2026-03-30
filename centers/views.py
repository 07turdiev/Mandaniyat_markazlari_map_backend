from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count

from .models import Region, District, CulturalCenter
from .serializers import (
    RegionSerializer, RegionListSerializer,
    DistrictSerializer, DistrictListSerializer,
    CulturalCenterSerializer, MapDataSerializer,
)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return RegionListSerializer
        return RegionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.annotate(
                district_count=Count('districts', distinct=True),
                center_count=Count('districts__centers', distinct=True),
            )
        else:
            qs = qs.prefetch_related('districts__centers')
        return qs


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.select_related('region')
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return DistrictListSerializer
        return DistrictSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        region_slug = self.request.query_params.get('region')
        if region_slug:
            qs = qs.filter(region__slug=region_slug)
        if self.action == 'list':
            qs = qs.annotate(center_count=Count('centers'))
        else:
            qs = qs.prefetch_related('centers')
        return qs


class CulturalCenterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CulturalCenter.objects.select_related('district', 'district__region')
    serializer_class = CulturalCenterSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        region = self.request.query_params.get('region')
        district = self.request.query_params.get('district')
        category = self.request.query_params.get('category')

        if region:
            qs = qs.filter(district__region__slug=region)
        if district:
            qs = qs.filter(district__slug=district)
        if category:
            qs = qs.filter(category=category)
        return qs


@api_view(['GET'])
def map_data(request):
    """Frontend uchun to'liq ma'lumot — data.json formati"""
    regions = Region.objects.prefetch_related('districts__centers').all()
    serializer = MapDataSerializer(regions, many=True)
    return Response({'regions': serializer.data})


@api_view(['GET'])
def statistics(request):
    """Umumiy statistika"""
    total_centers = CulturalCenter.objects.count()
    total_regions = Region.objects.count()
    total_districts = District.objects.count()

    by_category = {}
    for cat_code, cat_name in CulturalCenter.CATEGORY_CHOICES:
        by_category[cat_code] = CulturalCenter.objects.filter(category=cat_code).count()

    by_condition = {}
    for cond_code, cond_name in CulturalCenter.CONDITION_CHOICES:
        by_condition[cond_code] = CulturalCenter.objects.filter(condition=cond_code).count()

    total_population = sum(Region.objects.values_list('population', flat=True))

    return Response({
        'total_centers': total_centers,
        'total_regions': total_regions,
        'total_districts': total_districts,
        'total_population': total_population,
        'by_category': by_category,
        'by_condition': by_condition,
    })
