import math
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
import weasyprint

from .models import Region, District, Mahalla, CulturalCenter, Slide, GuestHouse, ExemplaryCenter
from .serializers import (
    RegionSerializer, RegionListSerializer,
    DistrictSerializer, DistrictListSerializer,
    CulturalCenterSerializer, MapDataSerializer,
    MahallaSerializer, SlideSerializer, GuestHouseSerializer, ExemplaryCenterSerializer,
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
                mahalla_count=Count('districts__mahallas', distinct=True),
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

    total_mahallas = Mahalla.objects.count()
    total_population = sum(Region.objects.values_list('population', flat=True))

    return Response({
        'total_centers': total_centers,
        'total_regions': total_regions,
        'total_districts': total_districts,
        'total_mahallas': total_mahallas,
        'total_population': total_population,
        'by_category': by_category,
        'by_condition': by_condition,
    })


@extend_schema(
    summary="Sliderlar ro'yxati",
    description="Harita tugmalari uchun faol Sliderlarni qaytaradi",
    tags=['slides'],
)
@api_view(['GET'])
def slides_list(request):
    """Faol Sliderlar ro'yxati"""
    slides = Slide.objects.filter(is_active=True).prefetch_related('images')
    serializer = SlideSerializer(slides, many=True, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    summary="Mehmonxona taqdimoti",
    description="Mehmonxona ma'lumotlari va media fayllarini qaytaradi",
    tags=['guesthouse'],
)
@api_view(['GET'])
def guesthouse_detail(request):
    """Mehmonxona taqdimoti"""
    guesthouse = GuestHouse.objects.filter(is_active=True).prefetch_related('media').first()
    if not guesthouse:
        return Response(None)
    serializer = GuestHouseSerializer(guesthouse, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    summary="Namunali markaz taqdimoti",
    description="Namunali markaz ma'lumotlari va media fayllarini qaytaradi",
    tags=['exemplary-center'],
)
@api_view(['GET'])
def exemplary_center_detail(request):
    """Namunali markaz taqdimoti"""
    exemplary = ExemplaryCenter.objects.filter(is_active=True).prefetch_related('media').first()
    if not exemplary:
        return Response(None)
    serializer = ExemplaryCenterSerializer(exemplary, context={'request': request})
    return Response(serializer.data)


@staff_member_required
def ajax_translate(request):
    """Admin panel uchun: o'zbekchadan ruschaga tarjima"""
    import json
    from .translation import translate_text

    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body)
        text = body.get('text', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not text:
        return JsonResponse({'translated': ''})

    translated = translate_text(text)
    return JsonResponse({'translated': translated or ''})


@staff_member_required
def ajax_centers_by_district(request, district_id):
    """Admin panel uchun: tumanga tegishli markazlar (dublikat tekshirish uchun)"""
    centers = CulturalCenter.objects.filter(district_id=district_id).values('id', 'name')
    return JsonResponse(list(centers), safe=False)


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


@extend_schema(
    summary="Madaniyat markazi pasportini PDF shaklida yuklab olish",
    description="Markaz pasportini frontend dizayni kabi PDF generatsiya qiladi",
    tags=['centers'],
)
@api_view(['GET'])
def passport_pdf(request, pk):
    """PDF pasport generatsiyasi"""
    center = get_object_or_404(CulturalCenter.objects.select_related('district', 'district__region', 'mahalla'), pk=pk)

    # 1. Rasmni tayyorlash — faqat bitta (birinchi) rasm
    image = None
    if center.has_own_building is not False:
        first_img = center.images.all().order_by('order').first()
        if first_img:
            try:
                image = 'file://' + first_img.image.path
            except Exception:
                image = None
                
    # Kategoriya dizayni
    categories_info = {
        'vazirlik': {'label': 'Vazirlik tarkibida qoladi', 'color': '#2E7D32'},
        'hokimlik': {'label': "Hokimlikka o'tkaziladi", 'color': '#1565C0'},
        'dxsh': {'label': 'DXSH', 'color': '#73C3EB'},
        'tugatiladi': {'label': 'Tugatiladi', 'color': '#C62828'},
    }
    cat_info = categories_info.get(center.category, {'label': center.category, 'color': '#999'})

    # Holat dizayni
    conditions_info = {
        'Yaxshi': {'label': 'Yaxshi', 'class': 'cond-good'},
        "O'rtacha": {'label': "O'rtacha", 'class': 'cond-mid'},
        'Avariya holatida': {'label': 'Avariya holatida', 'class': 'cond-bad'},
        'Tamir talab': {'label': 'Tamir talab', 'class': 'cond-repair'},
    }
    cond_info = conditions_info.get(center.condition, {'label': center.condition, 'class': ''})

    context = {
        'c': center,
        'image': image,
        'category_label': cat_info['label'],
        'category_color': cat_info['color'],
        'condition_label': cond_info['label'],
        'condition_class': cond_info['class'],
    }

    # HTML shablonidan string yaratish
    html_string = render_to_string('centers/passport_pdf.html', context, request=request)
    
    # WeasyPrint PDF qaytarish
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="passport_{center.id}.pdf"'
    
    return response
