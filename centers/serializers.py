from rest_framework import serializers
from .models import Region, District, Mahalla, CulturalCenter


class MahallaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mahalla
        fields = ['id', 'name', 'tin', 'soato', 'code', 'population']


class CulturalCenterSerializer(serializers.ModelSerializer):
    region_id = serializers.CharField(source='district.region.slug', read_only=True)
    region_name = serializers.CharField(source='district.region.name', read_only=True)
    district_id = serializers.CharField(source='district.slug', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    mahalla_name = serializers.CharField(source='mahalla.name', read_only=True, default='')
    mahalla_population = serializers.IntegerField(source='mahalla.population', read_only=True, default=0)

    class Meta:
        model = CulturalCenter
        fields = [
            'id', 'name', 'category', 'lat', 'lng', 'address',
            'director', 'phone', 'employees', 'capacity', 'built_year',
            'condition', 'area_sqm', 'description', 'image',
            'mahalla', 'mahalla_name', 'mahalla_population',
            'region_id', 'region_name', 'district_id', 'district_name',
        ]


class DistrictSerializer(serializers.ModelSerializer):
    centers = CulturalCenterSerializer(many=True, read_only=True)

    class Meta:
        model = District
        fields = ['id', 'slug', 'name', 'soato', 'population', 'centers']


class DistrictListSerializer(serializers.ModelSerializer):
    center_count = serializers.IntegerField(read_only=True)
    mahalla_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = District
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center_count', 'mahalla_count']


class RegionSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)
    center = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center', 'districts']

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]


class RegionListSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()
    district_count = serializers.IntegerField(read_only=True)
    center_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center', 'district_count', 'center_count']

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]


class MapDataSerializer(serializers.ModelSerializer):
    """Frontend uchun to'liq data.json formatidagi serializer"""
    districts = serializers.SerializerMethodField()
    center = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'name', 'population', 'center', 'districts']

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]

    def get_districts(self, obj):
        districts = obj.districts.prefetch_related('centers__mahalla').all()
        result = []
        for district in districts:
            centers = []
            for c in district.centers.all():
                centers.append({
                    'id': c.id,
                    'name': c.name,
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
                    'mahalla_name': c.mahalla.name if c.mahalla else '',
                    'mahalla_population': c.mahalla.population if c.mahalla else 0,
                })
            result.append({
                'id': district.slug,
                'name': district.name,
                'population': district.population,
                'centers': centers,
            })
        return result

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = instance.slug
        return ret
