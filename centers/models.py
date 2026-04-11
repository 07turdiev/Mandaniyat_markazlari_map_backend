from django.conf import settings
from django.db import models


class Region(models.Model):
    """Viloyat"""
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug (ID)")
    name = models.CharField(max_length=100, verbose_name="Nomi")
    soato = models.CharField(max_length=10, blank=True, db_index=True, verbose_name="SOATO kodi")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="Nomi (ruscha)")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="Nomi (inglizcha)")
    population = models.PositiveIntegerField(default=0, verbose_name="Aholi soni")
    center_lat = models.FloatField(default=0, verbose_name="Markaz (kenglik)")
    center_lng = models.FloatField(default=0, verbose_name="Markaz (uzunlik)")

    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    """Tuman"""
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name='districts', verbose_name="Viloyat"
    )
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug (ID)")
    name = models.CharField(max_length=100, verbose_name="Nomi")
    soato = models.CharField(max_length=10, blank=True, db_index=True, verbose_name="SOATO kodi")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="Nomi (ruscha)")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="Nomi (inglizcha)")
    population = models.PositiveIntegerField(default=0, verbose_name="Aholi soni")

    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Mahalla(models.Model):
    """Mahalla fuqarolar yig'ini"""
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='mahallas', verbose_name="Tuman"
    )
    name = models.CharField(max_length=200, verbose_name="Nomi")
    tin = models.CharField(max_length=20, unique=True, verbose_name="INN (TIN)")
    soato = models.CharField(max_length=15, blank=True, verbose_name="SOATO kodi")
    code = models.CharField(max_length=20, blank=True, verbose_name="Kod")
    name_uz = models.CharField(max_length=200, blank=True, verbose_name="Nomi (kirill)")
    name_ru = models.CharField(max_length=200, blank=True, verbose_name="Nomi (ruscha)")
    name_en = models.CharField(max_length=200, blank=True, verbose_name="Nomi (inglizcha)")
    population = models.PositiveIntegerField(default=0, verbose_name="Aholi soni")

    class Meta:
        verbose_name = "Mahalla"
        verbose_name_plural = "Mahallalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    """Faoliyat turi"""
    name = models.CharField(max_length=200, verbose_name="Nomi")

    class Meta:
        verbose_name = "Faoliyat turi"
        verbose_name_plural = "Faoliyat turlari"
        ordering = ['name']

    def __str__(self):
        return self.name


class CulturalCenter(models.Model):
    """Madaniyat markazi"""

    CATEGORY_CHOICES = [
        ('vazirlik', 'Vazirlik'),
        ('hokimlik', 'Hokimlik'),
        ('dxsh', 'DXSh'),
        ('tugatiladi', 'Tugatiladi'),
    ]

    CONDITION_CHOICES = [
        ('Yaxshi', 'Yaxshi'),
        ("O'rtacha", "O'rtacha"),
        ('Avariya holatida', 'Avariya holatida'),
        ('Tamir talab', 'Tamir talab'),
    ]

    # === Asosiy ma'lumotlar ===
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='centers', verbose_name="Tuman"
    )
    mahalla = models.ForeignKey(
        Mahalla, on_delete=models.SET_NULL, null=True,
        related_name='centers', verbose_name="Mahalla"
    )
    serving_mahallas = models.ManyToManyField(
        Mahalla, blank=True, related_name='served_by_centers', verbose_name="Xizmat qiluvchi mahallalar"
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")
    name_ru = models.CharField(max_length=255, blank=True, verbose_name="Nomi (ruscha)")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="Nomi (inglizcha)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Kategoriya")
    balance_holder = models.CharField(max_length=500, blank=True, verbose_name="Balansda saqlovchi")
    balance_holder_ru = models.CharField(max_length=500, blank=True, verbose_name="Balansda saqlovchi (ruscha)")
    activity_types = models.ManyToManyField(
        ActivityType, blank=True, related_name='centers', verbose_name="Faoliyat turlari"
    )
    lat = models.FloatField(verbose_name="Kenglik (latitude)")
    lng = models.FloatField(verbose_name="Uzunlik (longitude)")
    has_own_building = models.BooleanField(default=True, verbose_name="O'z binosiga ega")


    # === Obyekt haqida ma'lumot ===
    circles_count = models.PositiveIntegerField(default=0, verbose_name="To'garaklar soni")
    titled_teams_count = models.PositiveIntegerField(default=0, verbose_name="Unvonga ega jamoalar soni")
    library_activity_count = models.PositiveIntegerField(default=0, verbose_name="Kutubxona faoliyat soni")

    # === xadimlar ===
    management_staff = models.FloatField(default=0, verbose_name="Boshqaruv shtat birligi")
    creative_staff = models.FloatField(default=0, verbose_name="Ijodiy xadimlar soni")
    technical_staff = models.FloatField(default=0, verbose_name="Texnik xodimlar soni")
    titled_team_staff = models.FloatField(default=0, verbose_name="Unvonga ega jamoalar xodimlari soni")

    # === Obyekt tasnifi ===
    total_land_area = models.FloatField(default=0, verbose_name="Umumiy yer maydoni (ga)")
    building_area = models.FloatField(default=0, verbose_name="Bino va inshoatlar maydoni (kv.m)")
    buildings_count = models.PositiveIntegerField(default=0, verbose_name="Mavjud binolar soni")
    built_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Binolar qurilgan yil")
    building_floors = models.PositiveIntegerField(default=0, verbose_name="Bino qavati")
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default='Yaxshi', verbose_name="Bino holati"
    )
    building_technical_info = models.TextField(blank=True, verbose_name="Binoning texnik xarakteristikasi")
    building_technical_info_ru = models.TextField(blank=True, verbose_name="Binoning texnik xarakteristikasi (ruscha)")
    rooms_count = models.PositiveIntegerField(default=0, verbose_name="Xonalar soni")
    auditorium_seats = models.PositiveIntegerField(default=0, verbose_name="Tomosha zali (o’rin)")
    dining_area = models.FloatField(default=0, verbose_name="Ovqatlanish maydoni (kv.m)")
    restrooms_count = models.PositiveIntegerField(default=0, verbose_name="Xojatxonalar soni")
    additional_buildings_count = models.PositiveIntegerField(default=0, verbose_name="Qo'shimcha binolar soni")

    # === Kommunikatsiyalar ===
    has_heating = models.BooleanField(default=False, verbose_name="Isitish tizimi")
    has_electricity = models.BooleanField(default=False, verbose_name="Elektro-energiya")
    has_gas = models.BooleanField(default=False, verbose_name="Gaz")
    has_water = models.BooleanField(default=False, verbose_name="Ichimlik suvi")
    has_sewerage = models.BooleanField(default=False, verbose_name="Kanalizatsiya")

    # === Ajratilgan markaz ===
    is_featured = models.BooleanField(default=False, verbose_name="Ajratilgan markaz")

    # === Tizim ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    class Meta:
        verbose_name = "Madaniyat markazi"
        verbose_name_plural = "Madaniyat markazlari"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def region(self):
        return self.district.region

    @property
    def total_employees(self):
        return self.management_staff + self.creative_staff + self.technical_staff + self.titled_team_staff


class CulturalCenterImage(models.Model):
    """Madaniyat markazi qo'shimcha rasmlari"""
    center = models.ForeignKey(
        CulturalCenter, on_delete=models.CASCADE, related_name='images', verbose_name="Markaz"
    )
    image = models.ImageField(upload_to='centers/gallery/', verbose_name="Rasm")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Izoh")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Rasm"
        verbose_name_plural = "Rasmlar"
        ordering = ['order']

    def __str__(self):
        return f"{self.center.name} - rasm {self.order}"


class CulturalCenterProject(models.Model):
    """Madaniyat markazi loyihalari (rasm va videolar)"""

    MEDIA_TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
    ]

    center = models.ForeignKey(
        CulturalCenter, on_delete=models.CASCADE, related_name='projects', verbose_name="Markaz"
    )
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name="Turi")
    file = models.FileField(upload_to='centers/projects/', verbose_name="Fayl (rasm yoki video)")
    caption = models.CharField(max_length=500, blank=True, verbose_name="Izoh")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"
        ordering = ['order']

    def __str__(self):
        return f"{self.center.name} - {self.title}"


class Slide(models.Model):
    """Slidelar — haritadagi tugmalarga bog'langan"""
    title = models.CharField(max_length=255, verbose_name="Nomi")
    button_label = models.CharField(max_length=100, verbose_name="Tugma matni")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Slide"
        verbose_name_plural = "Slidelar"
        ordering = ['order']

    def __str__(self):
        return self.title


class SlideImage(models.Model):
    """Slide ichidagi rasmlar va videolar"""
    slide = models.ForeignKey(
        Slide, on_delete=models.CASCADE, related_name='images', verbose_name="Slide"
    )
    image = models.ImageField(upload_to='slides/images/', verbose_name="Rasm")
    video = models.FileField(
        upload_to='slides/videos/', blank=True, verbose_name="Video",
        help_text="Rasmga bog'langan video fayl (ixtiyoriy)"
    )
    caption = models.CharField(max_length=255, blank=True, verbose_name="Izoh")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Slide rasmi"
        verbose_name_plural = "Slide rasmlari"
        ordering = ['order']

    def __str__(self):
        return f"{self.slide.title} - rasm {self.order}"


class AdminProfile(models.Model):
    """Admin foydalanuvchi profili — viloyat va maydon darajasida tahrirlash ruxsatlari"""

    # CulturalCenter maydonlari bo'limlar bo'yicha guruhlangan
    FIELD_SECTIONS = {
        "Asosiy ma'lumotlar": [
            ('name', "Nomi"),
            ('name_ru', "Nomi (ruscha)"),
            ('name_en', "Nomi (inglizcha)"),
            ('category', "Kategoriya"),
            ('balance_holder', "Balansda saqlovchi"),
            ('balance_holder_ru', "Balansda saqlovchi (ruscha)"),
            ('district', "Tuman"),
            ('mahalla', "Mahalla"),
            ('serving_mahallas', "Xizmat qiluvchi mahallalar"),
            ('activity_types', "Faoliyat turlari"),
            ('has_own_building', "O'z binosiga ega"),
        ],
        "Joylashuv": [
            ('lat', "Kenglik (latitude)"),
            ('lng', "Uzunlik (longitude)"),
        ],
        "Obyekt haqida ma'lumot": [
            ('circles_count', "To'garaklar soni"),
            ('titled_teams_count', "Unvonga ega jamoalar soni"),
            ('library_activity_count', "Kutubxona faoliyat soni"),
        ],
        "xadimlar": [
            ('management_staff', "Boshqaruv shtat birligi"),
            ('creative_staff', "Ijodiy xadimlar soni"),
            ('technical_staff', "Texnik xodimlar soni"),
            ('titled_team_staff', "Unvonga ega jamoalar xodimlari soni"),
        ],
        "Obyekt tasnifi": [
            ('total_land_area', "Umumiy yer maydoni"),
            ('building_area', "Bino maydoni"),
            ('buildings_count', "Binolar soni"),
            ('built_year', "Qurilgan yil"),
            ('building_floors', "Bino qavati"),
            ('condition', "Bino holati"),
            ('building_technical_info', "Texnik xarakteristika"),
            ('building_technical_info_ru', "Texnik xarakteristika (ruscha)"),
            ('rooms_count', "Xonalar soni"),
            ('auditorium_seats', "Tomosha zali o'rinlari"),
            ('dining_area', "Ovqatlanish maydoni"),
            ('restrooms_count', "Xojatxonalar soni"),
            ('additional_buildings_count', "Qo'shimcha binolar soni"),
        ],
        "Kommunikatsiyalar": [
            ('has_heating', "Isitish tizimi"),
            ('has_electricity', "Elektro-energiya"),
            ('has_gas', "Gaz"),
            ('has_water', "Ichimlik suvi"),
            ('has_sewerage', "Kanalizatsiya"),
        ],
        "Ajratilgan markaz": [
            ('is_featured', "Ajratilgan markaz"),
        ],
    }

    # Barcha maydon nomlari (tezkor tekshirish uchun)
    ALL_FIELD_NAMES = []
    FIELD_CHOICES = []
    for _section, _fields in FIELD_SECTIONS.items():
        for _name, _label in _fields:
            ALL_FIELD_NAMES.append(_name)
            FIELD_CHOICES.append((_name, _label))

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='admin_profile', verbose_name="Foydalanuvchi"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Viloyat",
        help_text="Faqat shu viloyatdagi markazlarni ko'radi. Bo'sh = barcha viloyatlar"
    )
    allowed_fields = models.JSONField(
        default=list, blank=True,
        verbose_name="Tahrirlash mumkin bo'lgan maydonlar",
        help_text="Tanlangan maydonlarni admin tahrirlashi mumkin. Tanlanmaganlar faqat o'qish uchun."
    )
    can_edit_images = models.BooleanField(default=False, verbose_name="Rasmlar qo'shish/tahrirlash")
    can_edit_projects = models.BooleanField(default=False, verbose_name="Loyihalar qo'shish/tahrirlash")

    class Meta:
        verbose_name = "Admin profil"
        verbose_name_plural = "Admin profillar"

    def __str__(self):
        region_name = self.region.name if self.region else "Barcha viloyatlar"
        return f"{self.user.username} — {region_name}"

    def can_edit_field(self, field_name):
        """Berilgan maydonni tahrirlash mumkinligini tekshirish"""
        if not self.allowed_fields:
            return False
        return field_name in self.allowed_fields

    def get_readonly_fields(self):
        """Tahrirlash mumkin bo'lmagan maydonlar ro'yxati"""
        return [name for name in self.ALL_FIELD_NAMES if name not in (self.allowed_fields or [])]
