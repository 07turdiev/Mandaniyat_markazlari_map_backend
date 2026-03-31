import json

from django import forms
from django.contrib import admin
from .models import Region, District, Mahalla, CulturalCenter


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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.district_id:
            region = self.instance.district.region
            self.fields['region'].initial = region.id
            self.fields['district'].queryset = District.objects.filter(region=region)
            self.fields['mahalla'].queryset = Mahalla.objects.filter(district=self.instance.district)
        elif self.data.get('region'):
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                self.fields['district'].queryset = District.objects.none()
            try:
                district_id = int(self.data.get('district'))
                self.fields['mahalla'].queryset = Mahalla.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                self.fields['mahalla'].queryset = Mahalla.objects.none()
        else:
            self.fields['district'].queryset = District.objects.none()
            self.fields['mahalla'].queryset = Mahalla.objects.none()


@admin.register(CulturalCenter)
class CulturalCenterAdmin(admin.ModelAdmin):
    form = CulturalCenterForm
    change_form_template = 'admin/centers/culturalcenter/change_form.html'
    list_display = [
        'name', 'category', 'get_region', 'district', 'mahalla',
        'condition', 'employees', 'capacity', 'built_year',
    ]
    list_filter = ['category', 'condition', 'district__region']
    search_fields = ['name', 'address', 'director', 'district__name', 'district__region__name']
    list_select_related = ['district', 'district__region', 'mahalla']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'category', 'region', 'district', 'mahalla', 'condition', 'image')
        }),
        ('Joylashuv', {
            'fields': ('lat', 'lng', 'address')
        }),
        ("Boshqaruv ma'lumotlari", {
            'fields': ('director', 'phone', 'employees', 'capacity', 'built_year', 'area_sqm')
        }),
        ('Tavsif', {
            'fields': ('description',)
        }),
        ("Tizim ma'lumotlari", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description="Viloyat", ordering='district__region__name')
    def get_region(self, obj):
        return obj.district.region.name

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        districts_by_region = {}
        for d in District.objects.all().order_by('name'):
            districts_by_region.setdefault(d.region_id, []).append(
                {'id': d.id, 'name': d.name}
            )

        mahallas_by_district = {}
        for m in Mahalla.objects.all().order_by('name'):
            mahallas_by_district.setdefault(m.district_id, []).append(
                {'id': m.id, 'name': m.name}
            )

        extra_context['districts_json'] = json.dumps(districts_by_region)
        extra_context['mahallas_json'] = json.dumps(mahallas_by_district)

        return super().changeform_view(request, object_id, form_url, extra_context)
