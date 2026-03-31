"""
Frontend data.json faylidan madaniyat markazlari ma'lumotlarini import qiladi.
SOATO tumanlar allaqachon import qilingan bo'lishi kerak (import_soato).

Foydalanish:
    python manage.py import_data /path/to/data.json
"""
import json
from django.core.management.base import BaseCommand
from centers.models import Region, District, Mahalla, CulturalCenter


class Command(BaseCommand):
    help = "data.json faylidan madaniyat markazlari ma'lumotlarini import qilish"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help="data.json fayl yo'li")

    def handle(self, *args, **options):
        with open(options['file'], 'r', encoding='utf-8') as f:
            data = json.load(f)

        regions_data = data.get('regions', [])
        center_count = 0

        for r in regions_data:
            try:
                region = Region.objects.get(slug=r['id'])
            except Region.DoesNotExist:
                self.stderr.write(f"Viloyat topilmadi: {r['id']} — avval import_soato ni ishga tushiring")
                continue

            # data.json dagi population va koordinatalarni yangilash
            center_coords = r.get('center', [0, 0])
            region.population = r.get('population', region.population)
            region.center_lat = center_coords[0] if len(center_coords) > 0 else region.center_lat
            region.center_lng = center_coords[1] if len(center_coords) > 1 else region.center_lng
            region.save()

            for d in r.get('districts', []):
                # data.json dagi tuman slugini SOATO tumanga alias sifatida saqlash
                district, created = District.objects.get_or_create(
                    slug=d['id'],
                    defaults={
                        'region': region,
                        'name': d['name'],
                        'population': d.get('population', 0),
                        'soato': '',
                    }
                )
                if not created:
                    district.name = d['name']
                    district.population = d.get('population', 0) or district.population
                    district.save()

                for c in d.get('centers', []):
                    # Mahallani topishga urinish
                    mahalla = None
                    mahalla_id = c.get('mahalla_id', '')
                    if mahalla_id:
                        mahalla = Mahalla.objects.filter(tin=mahalla_id).first()
                        if not mahalla:
                            mahalla = Mahalla.objects.filter(code=mahalla_id).first()

                    CulturalCenter.objects.update_or_create(
                        id=c['id'],
                        defaults={
                            'district': district,
                            'mahalla': mahalla,
                            'name': c['name'],
                            'category': c.get('category', 'vazirlik'),
                            'lat': c.get('lat', 0),
                            'lng': c.get('lng', 0),
                            'address': c.get('address', ''),
                            'director': c.get('director', ''),
                            'phone': c.get('phone', ''),
                            'employees': c.get('employees', 0),
                            'capacity': c.get('capacity', 0),
                            'built_year': c.get('built_year'),
                            'condition': c.get('condition', 'Yaxshi'),
                            'area_sqm': c.get('area_sqm', 0),
                            'description': c.get('description', ''),
                        }
                    )
                    center_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import tugadi: {center_count} madaniyat markazi"
        ))
