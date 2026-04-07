import json

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from .models import Region, District, Mahalla, CulturalCenter, CulturalCenterImage, ActivityType, AdminProfile


# ============================================================
# Foydalanuvchilar va Rollar (Guruhlar) boshqaruvi
# ============================================================

admin.site.unregister(User)
admin.site.unregister(Group)


class GroupPermissionForm(forms.ModelForm):
    """Faqat centers ilovasiga tegishli ruxsatlarni ko'rsatish"""

    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'permissions' in self.fields:
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType

            # Faqat centers ilovasi + auth modellari uchun ruxsatlar
            allowed_apps = ['centers', 'auth']
            ct_ids = ContentType.objects.filter(app_label__in=allowed_apps).values_list('id', flat=True)
            self.fields['permissions'].queryset = Permission.objects.filter(
                content_type_id__in=ct_ids
            ).select_related('content_type')


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    form = GroupPermissionForm
    list_display = ['name', 'user_count', 'permission_count']

    @admin.display(description="Foydalanuvchilar")
    def user_count(self, obj):
        return obj.user_set.count()

    @admin.display(description="Ruxsatlar soni")
    def permission_count(self, obj):
        return obj.permissions.count()


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name = "Admin profil"
    verbose_name_plural = "Admin profil"
    fieldsets = (
        ("Viloyat cheklovi", {
            'fields': ('region',),
            'description': "Bo'sh qoldirilsa — barcha viloyatlardagi markazlarni ko'radi",
        }),
        ("Tahrirlash mumkin bo'lgan bo'limlar", {
            'fields': (
                'can_edit_basic', 'can_edit_location', 'can_edit_about',
                'can_edit_staff', 'can_edit_classification', 'can_edit_utilities',
            ),
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'is_active', 'is_staff', 'get_groups', 'get_region']
    list_filter = ['is_staff', 'is_active', 'groups']
    inlines = [AdminProfileInline]

    fieldsets = (
        ("Kirish ma'lumotlari", {
            'fields': ('username', 'password')
        }),
        ("Shaxsiy ma'lumotlar", {
            'fields': ('first_name', 'last_name')
        }),
        ("Ruxsatlar", {
            'fields': ('is_active', 'is_staff', 'groups'),
            'description': "Foydalanuvchini guruhga qo'shing. Guruh orqali ruxsatlar beriladi.",
        }),
    )

    add_fieldsets = (
        ("Yangi foydalanuvchi", {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ("Ruxsatlar", {
            'fields': ('is_active', 'is_staff', 'groups'),
        }),
    )

    filter_horizontal = ['groups']

    @admin.display(description="Guruhlar")
    def get_groups(self, obj):
        return ", ".join(g.name for g in obj.groups.all()) or "—"

    @admin.display(description="Viloyat")
    def get_region(self, obj):
        profile = getattr(obj, 'admin_profile', None)
        if profile and profile.region:
            return profile.region.name
        return "Barchasi"


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0
    fields = ['slug', 'name', 'soato', 'population']
    show_change_link = True


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'soato', 'population', 'district_count', 'center_count']
    search_fields = ['name', 'soato']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DistrictInline]

    @admin.display(description="Tumanlar soni")
    def district_count(self, obj):
        return obj.districts.count()

    @admin.display(description="Markazlar soni")
    def center_count(self, obj):
        return CulturalCenter.objects.filter(district__region=obj).count()



@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'soato', 'population', 'mahalla_count', 'center_count']
    list_filter = ['region']
    search_fields = ['name', 'soato', 'region__name']
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description="Mahallalar")
    def mahalla_count(self, obj):
        return obj.mahallas.count()

    @admin.display(description="Markazlar")
    def center_count(self, obj):
        return obj.centers.count()



@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'tin', 'soato', 'population']
    list_filter = ['district__region', 'district']
    search_fields = ['name', 'tin', 'soato', 'name_ru']
    list_select_related = ['district', 'district__region']
    raw_id_fields = ['district']


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class CulturalCenterForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Viloyat",
        required=False,
        widget=forms.Select(attrs={'id': 'id_region'}),
    )

    class Meta:
        model = CulturalCenter
        fields = '__all__'
        widgets = {
            'district': forms.Select(attrs={'id': 'id_district'}),
            'mahalla': forms.Select(attrs={'id': 'id_mahalla'}),
            'activity_types': forms.CheckboxSelectMultiple(),
            'serving_mahallas': forms.SelectMultiple(attrs={'id': 'id_serving_mahallas', 'size': 15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Yangi markaz qo'shishda barcha faoliyat turlarini tanlangan qilish
        if not self.instance.pk:
            self.fields['activity_types'].initial = ActivityType.objects.values_list('id', flat=True)

        if self.data.get('district'):
            # POST yuborilganda — yuborilgan tuman asosida queryset qurish
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                self.fields['district'].queryset = District.objects.all()
            try:
                district_id = int(self.data.get('district'))
                district_mahallas = Mahalla.objects.filter(district_id=district_id)
                self.fields['mahalla'].queryset = district_mahallas
                self.fields['serving_mahallas'].queryset = district_mahallas
            except (ValueError, TypeError):
                self.fields['mahalla'].queryset = Mahalla.objects.none()
                self.fields['serving_mahallas'].queryset = Mahalla.objects.none()
            if self.instance.pk and self.instance.district_id:
                self.fields['region'].initial = self.data.get('region')
        elif self.instance and self.instance.pk and self.instance.district_id:
            # Mavjud markazni ochishda — saqlangan tuman asosida
            region = self.instance.district.region
            self.fields['region'].initial = region.id
            self.fields['district'].queryset = District.objects.filter(region=region)
            self.fields['mahalla'].queryset = Mahalla.objects.filter(district=self.instance.district)
            self.fields['serving_mahallas'].queryset = Mahalla.objects.filter(district=self.instance.district)
        else:
            self.fields['district'].queryset = District.objects.none()
            self.fields['mahalla'].queryset = Mahalla.objects.none()
            self.fields['serving_mahallas'].queryset = Mahalla.objects.none()


class CulturalCenterImageInline(admin.TabularInline):
    model = CulturalCenterImage
    extra = 1
    fields = ['image', 'caption', 'order']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            last_order = obj.images.order_by('-order').values_list('order', flat=True).first()
            formset.form.base_fields['order'].initial = (last_order or 0) + 1
        else:
            formset.form.base_fields['order'].initial = 1
        return formset


@admin.register(CulturalCenter)
class CulturalCenterAdmin(admin.ModelAdmin):
    form = CulturalCenterForm
    change_form_template = 'admin/centers/culturalcenter/change_form.html'
    list_display = [
        'name', 'category', 'get_region', 'district',
        'condition', 'total_employees',
    ]
    list_filter = ['category', 'condition', 'district__region', 'activity_types']
    search_fields = ['name', 'district__name', 'district__region__name']
    list_select_related = ['district', 'district__region', 'mahalla']
    inlines = [CulturalCenterImageInline]
    readonly_fields = ['created_at', 'updated_at']

    # Bo'lim nomlari va ularga tegishli maydonlar
    SECTION_FIELDS = {
        'basic': [
            'name', 'name_ru', 'category', 'balance_holder', 'balance_holder_ru',
            'region', 'district', 'mahalla', 'serving_mahallas',
            'activity_types', 'has_own_building',
        ],
        'location': ['lat', 'lng'],
        'about': ['circles_count', 'titled_teams_count', 'library_activity_count'],
        'staff': ['management_staff', 'creative_staff', 'technical_staff', 'titled_team_staff'],
        'classification': [
            'total_land_area', 'building_area', 'buildings_count',
            'built_year', 'building_floors', 'condition',
            'building_technical_info', 'building_technical_info_ru', 'rooms_count',
            'auditorium_seats', 'dining_area',
            'restrooms_count', 'additional_buildings_count',
        ],
        'utilities': ['has_heating', 'has_electricity', 'has_gas', 'has_water', 'has_sewerage'],
    }

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': (
                'name', 'name_ru',
                'category', 'balance_holder', 'balance_holder_ru',
                'region', 'district', 'mahalla', 'serving_mahallas',
                'activity_types',
                'has_own_building',
            )
        }),
        ('Joylashuv', {
            'fields': ('lat', 'lng')
        }),
        ("Obyekt haqida ma'lumot", {
            'fields': ('circles_count', 'titled_teams_count', 'library_activity_count')
        }),
        ('Hodimlar', {
            'fields': (
                'management_staff', 'creative_staff',
                'technical_staff', 'titled_team_staff',
            )
        }),
        ('Obyekt tasnifi', {
            'fields': (
                'total_land_area', 'building_area', 'buildings_count',
                'built_year', 'building_floors', 'condition',
                'building_technical_info', 'building_technical_info_ru', 'rooms_count',
                'auditorium_seats', 'dining_area',
                'restrooms_count', 'additional_buildings_count',
            )
        }),
        ('Kommunikatsiyalar', {
            'fields': ('has_heating', 'has_electricity', 'has_gas', 'has_water', 'has_sewerage'),
        }),
        ("Tizim ma'lumotlari", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def _get_profile(self, request):
        """Joriy foydalanuvchining admin profilini olish"""
        if request.user.is_superuser:
            return None
        return getattr(request.user, 'admin_profile', None)

    def get_queryset(self, request):
        """Foydalanuvchining viloyati bo'yicha markazlarni filtrlash"""
        qs = super().get_queryset(request)
        profile = self._get_profile(request)
        if profile and profile.region:
            qs = qs.filter(district__region=profile.region)
        return qs

    def get_readonly_fields(self, request, obj=None):
        """Profilda ruxsat berilmagan bo'limlar readonly bo'ladi"""
        readonly = list(super().get_readonly_fields(request, obj))
        profile = self._get_profile(request)
        if profile:
            section_map = {
                'basic': profile.can_edit_basic,
                'location': profile.can_edit_location,
                'about': profile.can_edit_about,
                'staff': profile.can_edit_staff,
                'classification': profile.can_edit_classification,
                'utilities': profile.can_edit_utilities,
            }
            for section, can_edit in section_map.items():
                if not can_edit:
                    readonly.extend(self.SECTION_FIELDS[section])
        return readonly

    @admin.display(description="Viloyat", ordering='district__region__name')
    def get_region(self, obj):
        return obj.district.region.name

    @admin.display(description="Hodimlar")
    def total_employees(self, obj):
        return obj.total_employees

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        profile = self._get_profile(request)

        districts_qs = District.objects.all().order_by('name')
        mahallas_qs = Mahalla.objects.all().order_by('name')

        # Viloyat bo'yicha cheklangan bo'lsa — faqat o'sha viloyat ma'lumotlari
        if profile and profile.region:
            districts_qs = districts_qs.filter(region=profile.region)
            mahallas_qs = mahallas_qs.filter(district__region=profile.region)

        districts_by_region = {}
        for d in districts_qs:
            districts_by_region.setdefault(d.region_id, []).append(
                {'id': d.id, 'name': d.name}
            )

        mahallas_by_district = {}
        for m in mahallas_qs:
            mahallas_by_district.setdefault(m.district_id, []).append(
                {'id': m.id, 'name': m.name}
            )

        extra_context['districts_json'] = json.dumps(districts_by_region)
        extra_context['mahallas_json'] = json.dumps(mahallas_by_district)

        return super().changeform_view(request, object_id, form_url, extra_context)
