"""
tuman.json va Mahalla.json fayllaridan SOATO ma'lumotlarini import qiladi.
soatoMap.js dagi slug mapping ham ishlatiladi.

Foydalanish:
    python manage.py import_soato /path/to/frontend/src/data/
"""
import json
from django.core.management.base import BaseCommand
from centers.models import Region, District, Mahalla


# soatoMap.js dan olingan SOATO → slug mapping
REGION_SOATO_MAP = {
    '1703': 'andijon',
    '1706': 'buxoro',
    '1708': 'jizzax',
    '1710': 'qashqadaryo',
    '1712': 'navoiy',
    '1714': 'namangan',
    '1718': 'samarqand',
    '1722': 'surxondaryo',
    '1724': 'sirdaryo',
    '1726': 'toshkent-shahri',
    '1727': 'toshkent-viloyati',
    '1730': 'fargona',
    '1733': 'xorazm',
    '1735': 'qoraqalpogiston',
}

REGION_NAMES_UZ = {
    '1703': 'Andijon viloyati',
    '1706': 'Buxoro viloyati',
    '1708': 'Jizzax viloyati',
    '1710': 'Qashqadaryo viloyati',
    '1712': 'Navoiy viloyati',
    '1714': 'Namangan viloyati',
    '1718': 'Samarqand viloyati',
    '1722': 'Surxondaryo viloyati',
    '1724': 'Sirdaryo viloyati',
    '1726': 'Toshkent shahri',
    '1727': 'Toshkent viloyati',
    '1730': "Farg'ona viloyati",
    '1733': 'Xorazm viloyati',
    '1735': "Qoraqalpog'iston Respublikasi",
}


class Command(BaseCommand):
    help = "tuman.json va Mahalla.json dan SOATO ma'lumotlarini import qilish"

    def add_arguments(self, parser):
        parser.add_argument('data_dir', type=str, help="Frontend data papkasi yo'li (tuman.json va Mahalla.json joylashgan)")

    def handle(self, *args, **options):
        data_dir = options['data_dir'].rstrip('/')

        # 1. tuman.json dan viloyat va tumanlarni import qilish
        with open(f'{data_dir}/tuman.json', 'r', encoding='utf-8') as f:
            tumans = json.load(f)

        # Avval viloyatlarni yaratish/yangilash
        regions_ru = {}  # soato -> rus nomi
        districts_data = []

        for item in tumans:
            rid = item['RegionID']
            rname = item['RegionNane']
            if len(rid) == 4:
                regions_ru[rid] = rname
            else:
                # Bu tuman, parent viloyat soato = rid[:4]
                districts_data.append({
                    'soato': rid,
                    'name_ru': rname,
                    'region_soato': rid[:4],
                })

        region_count = 0
        for soato, slug in REGION_SOATO_MAP.items():
            region, created = Region.objects.update_or_create(
                soato=soato,
                defaults={
                    'slug': slug,
                    'name': REGION_NAMES_UZ.get(soato, slug),
                    'name_ru': regions_ru.get(soato, ''),
                }
            )
            region_count += 1

        self.stdout.write(f"Viloyatlar: {region_count}")

        # Tumanlarni import qilish
        district_count = 0
        for d in districts_data:
            region_soato = d['region_soato']
            try:
                region = Region.objects.get(soato=region_soato, soato__gt='')
            except Region.DoesNotExist:
                self.stderr.write(f"Viloyat topilmadi: {region_soato}")
                continue

            slug = f"{region.slug}-{d['soato']}"
            District.objects.update_or_create(
                soato=d['soato'],
                defaults={
                    'region': region,
                    'slug': slug,
                    'name': d['name_ru'],  # hozircha ruscha, keyin yangilanadi
                    'name_ru': d['name_ru'],
                }
            )
            district_count += 1

        self.stdout.write(f"Tumanlar: {district_count}")

        # 2. Mahalla.json dan mahallalarni import qilish
        with open(f'{data_dir}/Mahalla.json', 'r', encoding='utf-8') as f:
            mahallas = json.load(f)

        mahalla_count = 0
        skipped = 0
        for m in mahallas:
            district_soato = m.get('district_soato', '')
            try:
                district = District.objects.get(soato=district_soato)
            except District.DoesNotExist:
                skipped += 1
                continue

            Mahalla.objects.update_or_create(
                tin=m['tin'],
                defaults={
                    'district': district,
                    'name': m.get('name_uz_latin', ''),
                    'soato': m.get('uzcad_code', ''),
                    'code': m.get('code', ''),
                    'name_uz': m.get('name_uz', ''),
                    'name_ru': m.get('name_ru', ''),
                    'name_en': m.get('name_en', ''),
                }
            )
            mahalla_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import tugadi: {region_count} viloyat, {district_count} tuman, {mahalla_count} mahalla (o'tkazib yuborilgan: {skipped})"
        ))
