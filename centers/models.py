from django.db import models


class Region(models.Model):
    """Viloyat"""
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug (ID)")
    name = models.CharField(max_length=100, verbose_name="Nomi")
    soato = models.CharField(max_length=10, blank=True, db_index=True, verbose_name="SOATO kodi")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="Nomi (ruscha)")
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


class CulturalCenter(models.Model):
    """Madaniyat markazi"""

    CATEGORY_CHOICES = [
        ('vazirlik', 'Vazirlik'),
        ('hokimlik', 'Hokimlik'),
        ('dxsh', 'DXSh'),
        ('sotiladi', 'Sotiladi'),
    ]

    CONDITION_CHOICES = [
        ('Yaxshi', 'Yaxshi'),
        ("O'rtacha", "O'rtacha"),
        ('Yomon', 'Yomon'),
        ('Tamir talab', 'Tamir talab'),
    ]

    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='centers', verbose_name="Tuman"
    )
    mahalla = models.ForeignKey(
        Mahalla, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='centers', verbose_name="Mahalla"
    )
    name = models.CharField(max_length=255, verbose_name="Nomi")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Kategoriya")
    lat = models.FloatField(verbose_name="Kenglik (latitude)")
    lng = models.FloatField(verbose_name="Uzunlik (longitude)")
    address = models.CharField(max_length=500, verbose_name="Manzil")
    director = models.CharField(max_length=200, blank=True, verbose_name="Rahbar")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    employees = models.PositiveIntegerField(default=0, verbose_name="Xodimlar soni")
    capacity = models.PositiveIntegerField(default=0, verbose_name="Sig'imi")
    built_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Qurilgan yili")
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default='Yaxshi', verbose_name="Holati"
    )
    area_sqm = models.PositiveIntegerField(default=0, verbose_name="Maydoni (kv.m)")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    image = models.ImageField(upload_to='centers/', blank=True, null=True, verbose_name="Rasm")
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
