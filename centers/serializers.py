from rest_framework import serializers
from .models import Region, District, Mahalla, CulturalCenter, CulturalCenterImage, CulturalCenterProject, ActivityType, Slide, SlideImage, GuestHouse, GuestHouseMedia
from .middleware import get_current_language


class TranslatedNameMixin:
    """Tilga qarab name maydonini qaytaradi"""

    def get_translated_name(self, obj):
        lang = get_current_language()
        if lang == 'uz':
            return obj.name
        if lang == 'uz-cyrl':
            return getattr(obj, 'name_uz', '') or obj.name
        if lang == 'ru':
            return getattr(obj, 'name_ru', '') or obj.name
        return obj.name


class MahallaSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Mahalla
        fields = ['id', 'name', 'tin', 'soato', 'code', 'population']

    def get_name(self, obj):
        return self.get_translated_name(obj)


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = ['id', 'name']


class SlideImageSerializer(serializers.ModelSerializer):
    caption = serializers.SerializerMethodField()

    class Meta:
        model = SlideImage
        fields = ['id', 'image', 'video', 'caption', 'order']

    def get_caption(self, obj):
        lang = get_current_language()
        if lang == 'uz-cyrl' and obj.caption_uz:
            return obj.caption_uz
        if lang == 'ru' and obj.caption_ru:
            return obj.caption_ru
        return obj.caption


class SlideSerializer(serializers.ModelSerializer):
    images = SlideImageSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    button_label = serializers.SerializerMethodField()

    class Meta:
        model = Slide
        fields = ['id', 'title', 'button_label', 'order', 'images']

    def get_title(self, obj):
        lang = get_current_language()
        if lang == 'uz-cyrl' and obj.title_uz:
            return obj.title_uz
        if lang == 'ru' and obj.title_ru:
            return obj.title_ru
        return obj.title

    def get_button_label(self, obj):
        lang = get_current_language()
        if lang == 'uz-cyrl' and obj.button_label_uz:
            return obj.button_label_uz
        if lang == 'ru' and obj.button_label_ru:
            return obj.button_label_ru
        return obj.button_label


class GuestHouseMediaSerializer(serializers.ModelSerializer):
    caption = serializers.SerializerMethodField()

    class Meta:
        model = GuestHouseMedia
        fields = ['id', 'media_type', 'image', 'video', 'caption', 'order']

    def get_caption(self, obj):
        lang = get_current_language()
        if lang == 'uz-cyrl' and obj.caption_uz:
            return obj.caption_uz
        if lang == 'ru' and obj.caption_ru:
            return obj.caption_ru
        return obj.caption


class GuestHouseSerializer(serializers.ModelSerializer):
    media = GuestHouseMediaSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()

    class Meta:
        model = GuestHouse
        fields = ['id', 'title', 'media']

    def get_title(self, obj):
        lang = get_current_language()
        if lang == 'uz-cyrl' and obj.title_uz:
            return obj.title_uz
        if lang == 'ru' and obj.title_ru:
            return obj.title_ru
        return obj.title


class CulturalCenterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalCenterImage
        fields = ['id', 'image', 'caption', 'order']


class CulturalCenterProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalCenterProject
        fields = ['id', 'title', 'media_type', 'file', 'caption', 'order']


class CulturalCenterSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    balance_holder = serializers.SerializerMethodField()
    map_url = serializers.SerializerMethodField()
    region_soato = serializers.CharField(source='district.region.soato', read_only=True)
    region_name = serializers.SerializerMethodField()
    district_soato = serializers.CharField(source='district.soato', read_only=True)
    district_name = serializers.SerializerMethodField()
    mahalla_name = serializers.SerializerMethodField()
    mahalla_population = serializers.IntegerField(source='mahalla.population', read_only=True, default=0)
    images = CulturalCenterImageSerializer(many=True, read_only=True)
    projects = CulturalCenterProjectSerializer(many=True, read_only=True)
    activity_types = ActivityTypeSerializer(many=True, read_only=True)
    serving_mahallas = MahallaSerializer(many=True, read_only=True)
    building_technical_info = serializers.SerializerMethodField()
    total_employees = serializers.IntegerField(read_only=True)

    class Meta:
        model = CulturalCenter
        fields = [
            'id', 'name', 'category', 'balance_holder', 'activity_types',
            'lat', 'lng', 'map_url',
            'has_own_building', 'is_featured', 'images', 'projects',
            # Obyekt haqida
            'circles_count', 'titled_teams_count', 'library_activity_count',
            # xadimlar
            'management_staff', 'creative_staff', 'technical_staff',
            'titled_team_staff', 'total_employees',
            # Obyekt tasnifi
            'total_land_area', 'building_area', 'buildings_count',
            'built_year', 'building_floors', 'condition',
            'building_technical_info', 'rooms_count',
            'auditorium_seats', 'dining_area',
            'restrooms_count', 'additional_buildings_count',
            # Kommunikatsiyalar
            'has_heating', 'has_electricity', 'has_gas', 'has_water', 'has_sewerage',
            # Bog'lanishlar
            'mahalla', 'mahalla_name', 'mahalla_population', 'serving_mahallas',
            'region_soato', 'region_name', 'district_soato', 'district_name',
        ]

    def get_name(self, obj):
        return self.get_translated_name(obj)

    def get_map_url(self, obj):
        return f'https://www.google.com/maps?q={obj.lat},{obj.lng}'

    def get_balance_holder(self, obj):
        lang = get_current_language()
        if lang == 'ru' and obj.balance_holder_ru:
            return obj.balance_holder_ru
        return obj.balance_holder

    def get_building_technical_info(self, obj):
        lang = get_current_language()
        if lang == 'ru' and obj.building_technical_info_ru:
            return obj.building_technical_info_ru
        return obj.building_technical_info

    def _get_name_for_lang(self, obj, lang):
        """Tilga qarab obyektdan nom olish"""
        if lang == 'uz':
            return obj.name
        if lang == 'uz-cyrl':
            return getattr(obj, 'name_uz', '') or obj.name
        if lang == 'ru':
            return getattr(obj, 'name_ru', '') or obj.name
        return obj.name

    def get_region_name(self, obj):
        lang = get_current_language()
        return self._get_name_for_lang(obj.district.region, lang)

    def get_district_name(self, obj):
        lang = get_current_language()
        return self._get_name_for_lang(obj.district, lang)

    def get_mahalla_name(self, obj):
        if not obj.mahalla:
            return ''
        lang = get_current_language()
        return self._get_name_for_lang(obj.mahalla, lang)


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
    mahalla_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'slug', 'name', 'soato', 'population', 'center', 'district_count', 'center_count', 'mahalla_count']

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

    def _resolve_name(self, obj, lang):
        """Tilga qarab obyektdan nom olish"""
        if lang == 'uz':
            return obj.name
        if lang == 'uz-cyrl':
            return getattr(obj, 'name_uz', '') or obj.name
        if lang == 'ru':
            return getattr(obj, 'name_ru', '') or obj.name
        return obj.name

    def get_districts(self, obj):
        lang = get_current_language()
        districts = obj.districts.prefetch_related(
            'centers__mahalla', 'centers__activity_types', 'centers__serving_mahallas'
        ).all()
        result = []
        for district in districts:
            d_name = self._resolve_name(district, lang)

            centers = []
            for c in district.centers.all():
                c_name = self._resolve_name(c, lang)

                m_name = ''
                if c.mahalla:
                    m_name = self._resolve_name(c.mahalla, lang)

                centers.append({
                    'id': c.id,
                    'name': c_name,
                    'category': c.category,
                    'is_featured': c.is_featured,
                    'balance_holder': c.balance_holder_ru if (lang == 'ru' and c.balance_holder_ru) else c.balance_holder,
                    'has_own_building': c.has_own_building,
                    'activity_types': [at.name for at in c.activity_types.all()],
                    'lat': c.lat,
                    'lng': c.lng,
                    'map_url': f'https://www.google.com/maps?q={c.lat},{c.lng}',
                    # Obyekt haqida
                    'circles_count': c.circles_count,
                    'titled_teams_count': c.titled_teams_count,
                    'library_activity_count': c.library_activity_count,
                    # xadimlar
                    'management_staff': c.management_staff,
                    'creative_staff': c.creative_staff,
                    'technical_staff': c.technical_staff,
                    'titled_team_staff': c.titled_team_staff,
                    'total_employees': c.total_employees,
                    # Obyekt tasnifi
                    'total_land_area': c.total_land_area,
                    'building_area': c.building_area,
                    'buildings_count': c.buildings_count,
                    'built_year': c.built_year,
                    'building_floors': c.building_floors,
                    'condition': c.condition,
                    'building_technical_info': c.building_technical_info_ru if (lang == 'ru' and c.building_technical_info_ru) else c.building_technical_info,
                    'rooms_count': c.rooms_count,
                    'auditorium_seats': c.auditorium_seats,
                    'dining_area': c.dining_area,
                    'restrooms_count': c.restrooms_count,
                    'additional_buildings_count': c.additional_buildings_count,
                    # Kommunikatsiyalar
                    'has_heating': c.has_heating,
                    'has_electricity': c.has_electricity,
                    'has_gas': c.has_gas,
                    'has_water': c.has_water,
                    'has_sewerage': c.has_sewerage,
                    'serving_mahallas': [
                        {'id': sm.id, 'name': self._resolve_name(sm, lang), 'tin': sm.tin}
                        for sm in c.serving_mahallas.all()
                    ],
                    # Mahalla
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
