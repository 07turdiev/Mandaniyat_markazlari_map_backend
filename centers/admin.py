from django.contrib import admin
from .models import Region, District, CulturalCenter


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0
    fields = ['slug', 'name', 'population']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'population', 'district_count', 'center_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DistrictInline]

    @admin.display(description="Tumanlar soni")
    def district_count(self, obj):
        return obj.districts.count()

    @admin.display(description="Markazlar soni")
    def center_count(self, obj):
        return CulturalCenter.objects.filter(district__region=obj).count()


class CenterInline(admin.StackedInline):
    model = CulturalCenter
    extra = 0
    fields = [
        'name', 'category', 'condition', 'lat', 'lng', 'address',
        'director', 'phone', 'employees', 'capacity', 'built_year',
        'area_sqm', 'description', 'image',
        'mahalla_id', 'mahalla_name', 'mahalla_population',
    ]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'slug', 'population', 'center_count']
    list_filter = ['region']
    search_fields = ['name', 'region__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CenterInline]

    @admin.display(description="Markazlar soni")
    def center_count(self, obj):
        return obj.centers.count()


@admin.register(CulturalCenter)
class CulturalCenterAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'get_region', 'district', 'condition',
        'employees', 'capacity', 'built_year',
    ]
    list_filter = ['category', 'condition', 'district__region']
    search_fields = ['name', 'address', 'director', 'district__name', 'district__region__name']
    list_select_related = ['district', 'district__region']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'category', 'district', 'condition', 'image')
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
        ("Mahalla ma'lumotlari", {
            'fields': ('mahalla_id', 'mahalla_name', 'mahalla_population')
        }),
        ("Tizim ma'lumotlari", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description="Viloyat", ordering='district__region__name')
    def get_region(self, obj):
        return obj.district.region.name
