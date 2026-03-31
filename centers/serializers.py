from rest_framework import serializers
from .models import Region, District, Mahalla, CulturalCenter, CulturalCenterImage
from .middleware import get_current_language


class TranslatedNameMixin:
    """Tilga qarab name maydonini qaytaradi"""

    def get_translated_name(self, obj):
        lang = get_current_language()
        if lang == 'uz':
            return obj.name
        field = f'name_{lang}'
        return getattr(obj, field, '') or obj.name


class MahallaSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Mahalla
        fields = ['id', 'name', 'tin', 'soato', 'code', 'population']

    def get_name(self, obj):
        return self.get_translated_name(obj)


class CulturalCenterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalCenterImage
        fields = ['id', 'image', 'caption', 'order']


class CulturalCenterSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    region_soato = serializers.CharField(source='district.region.soato', read_only=True)
    region_name = serializers.SerializerMethodField()
    district_soato = serializers.CharField(source='district.soato', read_only=True)
    district_name = serializers.SerializerMethodField()
    mahalla_name = serializers.SerializerMethodField()
    mahalla_population = serializers.IntegerField(source='mahalla.population', read_only=True, default=0)
    images = CulturalCenterImageSerializer(many=True, read_only=True)

    class Meta:
        model = CulturalCenter
        fields = [
            'id', 'name', 'category', 'lat', 'lng', 'address',
            'director', 'phone', 'employees', 'capacity', 'built_year',
            'condition', 'area_sqm', 'description', 'image', 'images',
            'mahalla', 'mahalla_name', 'mahalla_population',
            'region_soato', 'region_name', 'district_soato', 'district_name',
        ]

    def get_name(self, obj):
        return self.get_translated_name(obj)

    def get_region_name(self, obj):
        lang = get_current_language()
        region = obj.district.region
        if lang != 'uz':
            return getattr(region, f'name_{lang}', '') or region.name
        return region.name

    def get_district_name(self, obj):
        lang = get_current_language()
        district = obj.district
        if lang != 'uz':
            return getattr(district, f'name_{lang}', '') or district.name
        return district.name

    def get_mahalla_name(self, obj):
        if not obj.mahalla:
            return ''
        lang = get_current_language()
        if lang != 'uz':
            return getattr(obj.mahalla, f'name_{lang}', '') or obj.mahalla.name
        return obj.mahalla.name


class DistrictSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    centers = CulturalCenterSerializer(many=True, read_only=True)

    class Meta:
        model = District
        fields = ['id', 'slug', 'name', 'soato', 'population', 'centers']

    def get_name(self, obj):
        return self.get_translated_name(obj)


class DistrictListSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    center_count = serializers.IntegerField(read_only=True)
    mahalla_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = District
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center_count', 'mahalla_count']

    def get_name(self, obj):
        return self.get_translated_name(obj)


class RegionSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    districts = DistrictSerializer(many=True, read_only=True)
    center = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center', 'districts']

    def get_name(self, obj):
        return self.get_translated_name(obj)

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]


class RegionListSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    center = serializers.SerializerMethodField()
    district_count = serializers.IntegerField(read_only=True)
    center_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center', 'district_count', 'center_count']

    def get_name(self, obj):
        return self.get_translated_name(obj)

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]


class MapDataSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    """Frontend uchun to'liq data.json formatidagi serializer"""
    districts = serializers.SerializerMethodField()
    center = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'name', 'soato', 'population', 'center', 'districts']

    def get_name(self, obj):
        return self.get_translated_name(obj)

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]

    def get_districts(self, obj):
        lang = get_current_language()
        districts = obj.districts.prefetch_related('centers__mahalla').all()
        result = []
        for district in districts:
            d_name = district.name
            if lang != 'uz':
                d_name = getattr(district, f'name_{lang}', '') or district.name

            centers = []
            for c in district.centers.all():
                c_name = c.name
                if lang != 'uz':
                    c_name = getattr(c, f'name_{lang}', '') or c.name

                m_name = ''
                if c.mahalla:
                    m_name = c.mahalla.name
                    if lang != 'uz':
                        m_name = getattr(c.mahalla, f'name_{lang}', '') or c.mahalla.name

                centers.append({
                    'id': c.id,
                    'name': c_name,
                    'category': c.category,
                    'lat': c.lat,
                    'lng': c.lng,
                    'address': c.address,
                    'director': c.director,
                    'phone': c.phone,
                    'employees': c.employees,
                    'capacity': c.capacity,
                    'built_year': c.built_year,
                    'condition': c.condition,
                    'area_sqm': c.area_sqm,
                    'description': c.description,
                    'mahalla_id': c.mahalla.tin if c.mahalla else '',
                    'mahalla_name': m_name,
                    'mahalla_population': c.mahalla.population if c.mahalla else 0,
                })
            result.append({
                'soato': district.soato,
                'name': d_name,
                'population': district.population,
                'centers': centers,
            })
        return result

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['soato'] = instance.soato
        return ret
