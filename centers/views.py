from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Region, District, Mahalla, CulturalCenter
from .serializers import (
    RegionSerializer, RegionListSerializer,
    DistrictSerializer, DistrictListSerializer,
    CulturalCenterSerializer, MapDataSerializer,
    MahallaSerializer,
)

LANG_PARAM = OpenApiParameter(
    name='Accept-Language',
    location=OpenApiParameter.HEADER,
    description="Til / Language: uz (o'zbek), ru (ruscha), en (inglizcha)",
    required=False,
    type=str,
    enum=['uz', 'ru', 'en'],
)


@extend_schema_view(
    list=extend_schema(
        summary="Viloyatlar ro'yxati",
        description="Barcha viloyatlar ro'yxatini qaytaradi (tuman va markaz soni bilan)",
        tags=['regions'],
        parameters=[LANG_PARAM],
    ),
    retrieve=extend_schema(
        summary="Viloyat tafsilotlari",
        description="Bitta viloyatning to'liq ma'lumotlari (tumanlar va markazlar bilan)",
        tags=['regions'],
        parameters=[LANG_PARAM],
    ),
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


@extend_schema_view(
    list=extend_schema(
        summary="Tumanlar ro'yxati",
        description="Barcha tumanlar ro'yxati. `region` slug parametri bilan filtrlash mumkin",
        tags=['districts'],
        parameters=[
            LANG_PARAM,
            OpenApiParameter(name='region', description="Viloyat slug bo'yicha filtrlash", type=str),
        ],
    ),
    retrieve=extend_schema(
        summary="Tuman tafsilotlari",
        description="Bitta tumanning to'liq ma'lumotlari (markazlar bilan)",
        tags=['districts'],
        parameters=[LANG_PARAM],
    ),
)
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
            qs = qs.annotate(
                center_count=Count('centers'),
                mahalla_count=Count('mahallas'),
            )
        else:
            qs = qs.prefetch_related('centers')
        return qs


@extend_schema_view(
    list=extend_schema(
        summary="Mahallalar ro'yxati",
        description="Barcha mahallalar. `district` (SOATO) yoki `region` (SOATO) bilan filtrlash mumkin",
        tags=['mahallas'],
        parameters=[
            LANG_PARAM,
            OpenApiParameter(name='district', description="Tuman SOATO kodi bo'yicha filtrlash", type=str),
            OpenApiParameter(name='region', description="Viloyat SOATO kodi bo'yicha filtrlash", type=str),
        ],
    ),
    retrieve=extend_schema(
        summary="Mahalla tafsilotlari",
        tags=['mahallas'],
        parameters=[LANG_PARAM],
    ),
)
class MahallaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mahalla.objects.select_related('district', 'district__region')
    serializer_class = MahallaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        district = self.request.query_params.get('district')
        region = self.request.query_params.get('region')
        if district:
            qs = qs.filter(district__soato=district)
        elif region:
            qs = qs.filter(district__region__soato=region)
        return qs


@extend_schema_view(
    list=extend_schema(
        summary="Madaniyat markazlari ro'yxati",
        description="Barcha markazlar. `region`, `district` (slug), `category` bilan filtrlash mumkin",
        tags=['centers'],
        parameters=[
            LANG_PARAM,
            OpenApiParameter(name='region', description="Viloyat slug bo'yicha filtrlash", type=str),
            OpenApiParameter(name='district', description="Tuman slug bo'yicha filtrlash", type=str),
            OpenApiParameter(
                name='category',
                description="Kategoriya bo'yicha filtrlash",
                type=str,
                enum=['vazirlik', 'hokimlik', 'dxsh', 'tugatiladi'],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Madaniyat markazi tafsilotlari",
        tags=['centers'],
        parameters=[LANG_PARAM],
    ),
)
class CulturalCenterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CulturalCenter.objects.select_related('district', 'district__region', 'mahalla')
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


@extend_schema(
    summary="Xarita uchun to'liq ma'lumot",
    description="Frontend xaritasi uchun barcha viloyat, tuman va markazlar ma'lumotini qaytaradi",
    tags=['map'],
    parameters=[LANG_PARAM],
)
@api_view(['GET'])
def map_data(request):
    """Frontend uchun to'liq ma'lumot — data.json formati"""
    regions = Region.objects.prefetch_related('districts__centers').all()
    serializer = MapDataSerializer(regions, many=True)
    return Response({'regions': serializer.data})


@extend_schema(
    summary="Umumiy statistika",
    description="Markazlar soni, kategoriya va holat bo'yicha statistika",
    tags=['statistics'],
    parameters=[LANG_PARAM],
)
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


@staff_member_required
def ajax_districts(request, region_id):
    """Admin panel uchun: viloyatga tegishli tumanlar"""
    districts = District.objects.filter(region_id=region_id).order_by('name').values('id', 'name')
    return JsonResponse(list(districts), safe=False)


@staff_member_required
def ajax_mahallas(request, district_id):
    """Admin panel uchun: tumanga tegishli mahallalar"""
    mahallas = Mahalla.objects.filter(district_id=district_id).order_by('name').values('id', 'name')
    return JsonResponse(list(mahallas), safe=False)
