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
        ('Yomon', 'Yomon'),
        ('Tamir talab', 'Tamir talab'),
    ]

    # === Asosiy ma'lumotlar ===
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='centers', verbose_name="Tuman"
    )
    mahalla = models.ForeignKey(
        Mahalla, on_delete=models.SET_NULL, null=True, blank=True,
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
    map_url = models.URLField(max_length=1000, blank=True, verbose_name="Xarita havolasi (Google/Yandex)")
    has_own_building = models.BooleanField(default=True, verbose_name="O'z binosiga ega")
    image = models.ImageField(upload_to='centers/', blank=True, null=True, verbose_name="Rasm")

    # === Obyekt haqida ma'lumot ===
    circles_count = models.PositiveIntegerField(default=0, verbose_name="To'garaklar soni")
    titled_teams_count = models.PositiveIntegerField(default=0, verbose_name="Unvonga ega jamoalar soni")
    library_activity_count = models.PositiveIntegerField(default=0, verbose_name="Kutubxona faoliyat soni")

    # === Hodimlar ===
    management_staff = models.FloatField(default=0, verbose_name="Boshqaruv shtat birligi")
    creative_staff = models.PositiveIntegerField(default=0, verbose_name="Ijodiy hodimlar soni")
    technical_staff = models.PositiveIntegerField(default=0, verbose_name="Texnik xodimlar soni")
    titled_team_staff = models.PositiveIntegerField(default=0, verbose_name="Unvonga ega jamoalar xodimlari soni")

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
    auditorium_area = models.FloatField(default=0, verbose_name="Tomosha zali maydoni (kv.m)")
    dining_area = models.FloatField(default=0, verbose_name="Ovqatlanish maydoni (kv.m)")
    restrooms_count = models.PositiveIntegerField(default=0, verbose_name="Xojatxonalar soni")
    additional_buildings_count = models.PositiveIntegerField(default=0, verbose_name="Qo'shimcha binolar soni")

    # === Kommunikatsiyalar ===
    has_heating = models.BooleanField(default=False, verbose_name="Isitish tizimi")
    has_electricity = models.BooleanField(default=False, verbose_name="Elektro-energiya")
    has_gas = models.BooleanField(default=False, verbose_name="Gaz")
    has_water = models.BooleanField(default=False, verbose_name="Ichimlik suvi")
    has_sewerage = models.BooleanField(default=False, verbose_name="Kanalizatsiya")

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
        return int(self.management_staff) + self.creative_staff + self.technical_staff + self.titled_team_staff


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
