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


@admin.register(CulturalCenter)
class CulturalCenterAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'get_region', 'district', 'mahalla',
        'condition', 'employees', 'capacity', 'built_year',
    ]
    list_filter = ['category', 'condition', 'district__region']
    search_fields = ['name', 'address', 'director', 'district__name', 'district__region__name']
    list_select_related = ['district', 'district__region', 'mahalla']
    raw_id_fields = ['mahalla']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'category', 'district', 'mahalla', 'condition', 'image')
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
