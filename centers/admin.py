import json

from django import forms
from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import (
    Region, District, Mahalla, CulturalCenter, CulturalCenterImage,
    CulturalCenterProject, ActivityType, AdminProfile, Slide, SlideImage,
    GuestHouse, GuestHouseMedia, ExemplaryCenter, ExemplaryCenterMedia,
)


# ============================================================
# Admin loglar
# ============================================================

ACTION_NAMES = {
    ADDITION: "Qo'shdi",
    CHANGE: "O'zgartirdi",
    DELETION: "O'chirdi",
}


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'get_action', 'content_type', 'get_object', 'get_change_message']
    list_filter = ['action_flag', 'content_type', 'user']
    search_fields = ['object_repr', 'change_message', 'user__username']
    date_hierarchy = 'action_time'
    list_per_page = 50
    list_select_related = ['user', 'content_type']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Amal", ordering='action_flag')
    def get_action(self, obj):
        colors = {ADDITION: 'green', CHANGE: 'orange', DELETION: 'red'}
        color = colors.get(obj.action_flag, 'gray')
        label = ACTION_NAMES.get(obj.action_flag, '?')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)

    @admin.display(description="Obyekt")
    def get_object(self, obj):
        return obj.object_repr

    @admin.display(description="O'zgarishlar")
    def get_change_message(self, obj):
        return obj.get_change_message() or "—"


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


class GroupedCheckboxWidget(forms.Widget):
    """Bo'limlar bo'yicha guruhlangan checkbox widget"""

    template_name = 'admin/centers/widgets/grouped_checkboxes.html'

    def __init__(self, sections, attrs=None):
        super().__init__(attrs)
        self.sections = sections

    def render(self, name, value, attrs=None, renderer=None):
        """Loyiha template loader orqali rendering — Django widget renderer'ini chetlab o'tish"""
        from django.template.loader import render_to_string
        if value is None:
            value = []
        elif isinstance(value, str):
            try:
                import json
                value = json.loads(value)
            except (ValueError, TypeError):
                value = []
        context = {
            'widget': {
                'name': name,
                'sections': self.sections,
                'selected': set(value),
            }
        }
        return render_to_string(self.template_name, context)

    def value_from_datadict(self, data, files, name):
        if hasattr(data, 'getlist'):
            return data.getlist(name)
        return data.get(name, [])


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'allowed_fields' in self.fields:
            self.fields['allowed_fields'].widget = GroupedCheckboxWidget(
                sections=AdminProfile.FIELD_SECTIONS
            )
            self.fields['allowed_fields'].help_text = (
                "Belgilangan maydonlarni admin tahrirlashi mumkin. "
                "Belgilanmaganlar faqat o'qish uchun ko'rsatiladi."
            )


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    form = AdminProfileForm
    can_delete = False
    verbose_name = "Admin profil"
    verbose_name_plural = "Admin profil"
    fieldsets = (
        ("Viloyat cheklovi", {
            'fields': ('region',),
            'description': "Bo'sh qoldirilsa — barcha viloyatlardagi markazlarni ko'radi",
        }),
        ("Madaniyat markazi maydonlari ruxsatlari", {
            'fields': ('allowed_fields',),
            'description': "Har bir maydonni alohida bloklash yoki ruxsat berish mumkin",
        }),
        ("Rasmlar va Loyihalar", {
            'fields': ('can_edit_images', 'can_edit_projects'),
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


class ProfileReadOnlyMixin:
    """
    AdminProfile ga ega staff foydalanuvchilarga ko'rish ruxsatini beradi
    (lekin tahrirlash/qo'shish/o'chirish faqat superuser uchun).

    Buning yordamida administratorlar 403 xatosiz Region/District/Mahalla
    ma'lumotlarini ko'ra oladi (CulturalCenter form'i ishlashi uchun zarur).
    """

    def _has_profile_access(self, request):
        if request.user.is_superuser:
            return True
        return request.user.is_staff and hasattr(request.user, 'admin_profile')

    def has_module_permission(self, request):
        return self._has_profile_access(request)

    def has_view_permission(self, request, obj=None):
        return self._has_profile_access(request)

    def has_change_permission(self, request, obj=None):
        # Faqat superuser tahrirlay oladi (bu ma'lumotnoma)
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0
    fields = ['slug', 'name', 'soato', 'population']
    show_change_link = True


@admin.register(Region)
class RegionAdmin(ProfileReadOnlyMixin, admin.ModelAdmin):
    list_display = ['name', 'slug', 'soato', 'population', 'district_count', 'center_count']
    search_fields = ['name', 'soato']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DistrictInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            profile = getattr(request.user, 'admin_profile', None)
            if profile and profile.region:
                qs = qs.filter(id=profile.region.id)
        return qs

    @admin.display(description="Tumanlar soni")
    def district_count(self, obj):
        return obj.districts.count()

    @admin.display(description="Markazlar soni")
    def center_count(self, obj):
        return CulturalCenter.objects.filter(district__region=obj).count()



@admin.register(District)
class DistrictAdmin(ProfileReadOnlyMixin, admin.ModelAdmin):
    list_display = ['name', 'region', 'soato', 'population', 'mahalla_count', 'center_count']
    list_filter = ['region']
    search_fields = ['name', 'soato', 'region__name']
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            profile = getattr(request.user, 'admin_profile', None)
            if profile and profile.region:
                qs = qs.filter(region=profile.region)
        return qs

    @admin.display(description="Mahallalar")
    def mahalla_count(self, obj):
        return obj.mahallas.count()

    @admin.display(description="Markazlar")
    def center_count(self, obj):
        return obj.centers.count()



@admin.register(Mahalla)
class MahallaAdmin(ProfileReadOnlyMixin, admin.ModelAdmin):
    list_display = ['name', 'district', 'tin', 'soato', 'population']
    list_filter = ['district__region', 'district']
    search_fields = ['name', 'tin', 'soato', 'name_ru']
    list_select_related = ['district', 'district__region']
    raw_id_fields = ['district']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            profile = getattr(request.user, 'admin_profile', None)
            if profile and profile.region:
                qs = qs.filter(district__region=profile.region)
        return qs


@admin.register(ActivityType)
class ActivityTypeAdmin(ProfileReadOnlyMixin, admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class SlideImageInline(admin.TabularInline):
    model = SlideImage
    extra = 1
    fields = ['image', 'video', 'caption', 'caption_uz', 'caption_ru', 'order']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            last_order = obj.images.order_by('-order').values_list('order', flat=True).first()
            formset.form.base_fields['order'].initial = (last_order or 0) + 1
        else:
            formset.form.base_fields['order'].initial = 1
        return formset


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'button_label', 'order', 'is_active', 'image_count']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'button_label']
    fieldsets = [
        ("O'zbekcha (lotin)", {'fields': ['title', 'button_label']}),
        ("O'zbekcha (kirill)", {'fields': ['title_uz', 'button_label_uz'], 'classes': ['collapse']}),
        ("Ruscha", {'fields': ['title_ru', 'button_label_ru'], 'classes': ['collapse']}),
        ("Sozlamalar", {'fields': ['order', 'is_active']}),
    ]
    inlines = [SlideImageInline]

    @admin.display(description="Rasmlar soni")
    def image_count(self, obj):
        return obj.images.count()


class GuestHouseMediaForm(forms.ModelForm):
    class Meta:
        model = GuestHouseMedia
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        media_type = cleaned.get('media_type')
        image = cleaned.get('image')
        video = cleaned.get('video')

        if media_type == 'image' and not image:
            self.add_error('image', 'Rasm turida rasm yuklash majburiy.')
        if media_type == 'video' and not video:
            self.add_error('video', 'Video turida video yuklash majburiy.')
        return cleaned


class GuestHouseMediaInline(admin.TabularInline):
    model = GuestHouseMedia
    form = GuestHouseMediaForm
    extra = 1
    fields = ['media_type', 'image', 'video', 'caption', 'caption_uz', 'caption_ru', 'order']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            last_order = obj.media.order_by('-order').values_list('order', flat=True).first()
            formset.form.base_fields['order'].initial = (last_order or 0) + 1
        else:
            formset.form.base_fields['order'].initial = 1
        return formset


@admin.register(GuestHouse)
class GuestHouseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'media_count']
    fieldsets = [
        ("O'zbekcha (lotin)", {'fields': ['title']}),
        ("O'zbekcha (kirill)", {'fields': ['title_uz'], 'classes': ['collapse']}),
        ("Ruscha", {'fields': ['title_ru'], 'classes': ['collapse']}),
        ("Sozlamalar", {'fields': ['is_active']}),
    ]
    inlines = [GuestHouseMediaInline]

    @admin.display(description="Media soni")
    def media_count(self, obj):
        return obj.media.count()

    def has_add_permission(self, request):
        # Faqat bitta yozuv bo'lishi mumkin
        if GuestHouse.objects.exists():
            return False
        return super().has_add_permission(request)


class ExemplaryCenterMediaForm(forms.ModelForm):
    class Meta:
        model = ExemplaryCenterMedia
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        media_type = cleaned.get('media_type')
        image = cleaned.get('image')
        video = cleaned.get('video')

        if media_type == 'image' and not image:
            self.add_error('image', 'Rasm turida rasm yuklash majburiy.')
        if media_type == 'video' and not video:
            self.add_error('video', 'Video turida video yuklash majburiy.')
        return cleaned


class ExemplaryCenterMediaInline(admin.TabularInline):
    model = ExemplaryCenterMedia
    form = ExemplaryCenterMediaForm
    extra = 1
    fields = ['media_type', 'image', 'video', 'caption', 'caption_uz', 'caption_ru', 'order']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            last_order = obj.media.order_by('-order').values_list('order', flat=True).first()
            formset.form.base_fields['order'].initial = (last_order or 0) + 1
        else:
            formset.form.base_fields['order'].initial = 1
        return formset


@admin.register(ExemplaryCenter)
class ExemplaryCenterAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'media_count']
    fieldsets = [
        ("O'zbekcha (lotin)", {'fields': ['title']}),
        ("O'zbekcha (kirill)", {'fields': ['title_uz'], 'classes': ['collapse']}),
        ("Ruscha", {'fields': ['title_ru'], 'classes': ['collapse']}),
        ("Sozlamalar", {'fields': ['is_active']}),
    ]
    inlines = [ExemplaryCenterMediaInline]

    @admin.display(description="Media soni")
    def media_count(self, obj):
        return obj.media.count()

    def has_add_permission(self, request):
        # Faqat bitta yozuv bo'lishi mumkin
        if ExemplaryCenter.objects.exists():
            return False
        return super().has_add_permission(request)


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
        if not self.instance.pk and 'activity_types' in self.fields:
            self.fields['activity_types'].initial = ActivityType.objects.values_list('id', flat=True)

        # Maydonlar profil orqali bloklangan bo'lishi mumkin — xavfsiz yordamchi
        def set_qs(field_name, qs):
            if field_name in self.fields:
                self.fields[field_name].queryset = qs

        def set_initial(field_name, value):
            if field_name in self.fields:
                self.fields[field_name].initial = value

        if self.data.get('district'):
            # POST yuborilganda — yuborilgan tuman asosida queryset qurish
            try:
                region_id = int(self.data.get('region'))
                set_qs('district', District.objects.filter(region_id=region_id))
            except (ValueError, TypeError):
                set_qs('district', District.objects.all())
            try:
                district_id = int(self.data.get('district'))
                district_mahallas = Mahalla.objects.filter(district_id=district_id)
                set_qs('mahalla', district_mahallas)
                set_qs('serving_mahallas', district_mahallas)
            except (ValueError, TypeError):
                set_qs('mahalla', Mahalla.objects.none())
                set_qs('serving_mahallas', Mahalla.objects.none())
            if self.instance.pk and self.instance.district_id:
                set_initial('region', self.data.get('region'))
        elif self.instance and self.instance.pk and self.instance.district_id:
            # Mavjud markazni ochishda — saqlangan tuman asosida
            region = self.instance.district.region
            set_initial('region', region.id)
            set_qs('district', District.objects.filter(region=region))
            set_qs('mahalla', Mahalla.objects.filter(district=self.instance.district))
            set_qs('serving_mahallas', Mahalla.objects.filter(district=self.instance.district))
        else:
            set_qs('district', District.objects.none())
            set_qs('mahalla', Mahalla.objects.none())
            set_qs('serving_mahallas', Mahalla.objects.none())


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


class CulturalCenterProjectInline(admin.TabularInline):
    model = CulturalCenterProject
    extra = 1
    fields = ['title', 'media_type', 'file', 'caption', 'order']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            last_order = obj.projects.order_by('-order').values_list('order', flat=True).first()
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
        'condition', 'total_employees', 'is_featured', 'is_dxsh_project',
    ]
    list_filter = ['category', 'condition', 'district__region', 'activity_types', 'is_featured', 'is_dxsh_project']
    search_fields = ['name', 'district__name', 'district__region__name']
    list_select_related = ['district', 'district__region', 'mahalla']
    inlines = [CulturalCenterImageInline, CulturalCenterProjectInline]
    readonly_fields = ['created_at', 'updated_at']


    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': (
                'name', 'name_uz', 'name_ru',
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
        ('xadimlar', {
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
        ('DXSh loyiha', {
            'fields': ('is_dxsh_project',),
        }),
        ('Ajratilgan markaz', {
            'fields': ('is_featured',),
        }),
        ("Tizim ma'lumotlari", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    # === Permissions ===
    def _has_profile_access(self, request):
        if request.user.is_superuser:
            return True
        return request.user.is_staff and hasattr(request.user, 'admin_profile')

    def has_module_permission(self, request):
        return self._has_profile_access(request)

    def has_view_permission(self, request, obj=None):
        return self._has_profile_access(request)

    def has_change_permission(self, request, obj=None):
        return self._has_profile_access(request)

    def has_add_permission(self, request):
        return self._has_profile_access(request)

    def has_delete_permission(self, request, obj=None):
        # O'chirish faqat superuser uchun
        return request.user.is_superuser

    def _get_profile(self, request):
        """Joriy foydalanuvchining admin profilini olish"""
        if request.user.is_superuser:
            return None
        return getattr(request.user, 'admin_profile', None)

    def get_inlines(self, request, obj=None):
        """Rasmlar va loyihalar inline'larini profil asosida boshqarish"""
        profile = self._get_profile(request)
        inlines = []
        if not profile or profile.can_edit_images:
            inlines.append(CulturalCenterImageInline)
        if not profile or profile.can_edit_projects:
            inlines.append(CulturalCenterProjectInline)
        return inlines

    def get_queryset(self, request):
        """Foydalanuvchining viloyati bo'yicha markazlarni filtrlash"""
        qs = super().get_queryset(request)
        profile = self._get_profile(request)
        if profile and profile.region:
            qs = qs.filter(district__region=profile.region)
        return qs

    def get_readonly_fields(self, request, obj=None):
        """Profilda ruxsat berilmagan maydonlar readonly bo'ladi (har bir maydon alohida)"""
        readonly = list(super().get_readonly_fields(request, obj))
        profile = self._get_profile(request)
        if profile:
            readonly.extend(profile.get_readonly_fields())
        return readonly

    @admin.display(description="Viloyat", ordering='district__region__name')
    def get_region(self, obj):
        return obj.district.region.name

    @admin.display(description="xadimlar")
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
