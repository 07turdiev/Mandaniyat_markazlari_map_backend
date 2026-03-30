from rest_framework import serializers
from .models import Region, District, CulturalCenter


class CulturalCenterSerializer(serializers.ModelSerializer):
    region_id = serializers.CharField(source='district.region.slug', read_only=True)
    region_name = serializers.CharField(source='district.region.name', read_only=True)
    district_id = serializers.CharField(source='district.slug', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = CulturalCenter
        fields = [
            'id', 'name', 'category', 'lat', 'lng', 'address',
            'director', 'phone', 'employees', 'capacity', 'built_year',
            'condition', 'area_sqm', 'description', 'image',
            'mahalla_id', 'mahalla_name', 'mahalla_population',
            'region_id', 'region_name', 'district_id', 'district_name',
        ]


class DistrictSerializer(serializers.ModelSerializer):
    centers = CulturalCenterSerializer(many=True, read_only=True)

    class Meta:
        model = District
        fields = ['id', 'slug', 'name', 'population', 'centers']


class DistrictListSerializer(serializers.ModelSerializer):
    center_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = District
        fields = ['id', 'slug', 'name', 'population', 'center_count']


class RegionSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)
    center = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'population', 'center', 'districts']

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]


class RegionListSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()
    district_count = serializers.IntegerField(read_only=True)
    center_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'population', 'center', 'district_count', 'center_count']

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]


class MapDataSerializer(serializers.ModelSerializer):
    """Frontend uchun to'liq data.json formatidagi serializer"""
    districts = serializers.SerializerMethodField()
    center = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'name', 'population', 'center', 'districts']

    def get_id(self, obj):
        return obj.slug

    def get_center(self, obj):
        return [obj.center_lat, obj.center_lng]

    def get_districts(self, obj):
        districts = obj.districts.prefetch_related('centers').all()
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
                    'mahalla_id': c.mahalla_id,
                    'mahalla_name': c.mahalla_name,
                    'mahalla_population': c.mahalla_population,
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
