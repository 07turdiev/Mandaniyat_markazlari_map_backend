"""
Frontend data.json faylidan ma'lumotlarni import qiladi.

Foydalanish:
    python manage.py import_data /path/to/data.json
"""
import json
from django.core.management.base import BaseCommand
from centers.models import Region, District, CulturalCenter


class Command(BaseCommand):
    help = "data.json faylidan viloyat, tuman va madaniyat markazlari ma'lumotlarini import qilish"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help="data.json fayl yo'li")

    def handle(self, *args, **options):
        with open(options['file'], 'r', encoding='utf-8') as f:
            data = json.load(f)

        regions_data = data.get('regions', [])
        region_count = 0
        district_count = 0
        center_count = 0

        for r in regions_data:
            center_coords = r.get('center', [0, 0])
            region, _ = Region.objects.update_or_create(
                slug=r['id'],
                defaults={
                    'name': r['name'],
                    'population': r.get('population', 0),
                    'center_lat': center_coords[0] if len(center_coords) > 0 else 0,
                    'center_lng': center_coords[1] if len(center_coords) > 1 else 0,
                }
            )
            region_count += 1

            for d in r.get('districts', []):
                district, _ = District.objects.update_or_create(
                    slug=d['id'],
                    defaults={
                        'region': region,
                        'name': d['name'],
                        'population': d.get('population', 0),
                    }
                )
                district_count += 1

                for c in d.get('centers', []):
                    CulturalCenter.objects.update_or_create(
                        id=c['id'],
                        defaults={
                            'district': district,
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
                            'mahalla_id': c.get('mahalla_id', ''),
                            'mahalla_name': c.get('mahalla_name', ''),
                            'mahalla_population': c.get('mahalla_population', 0),
                        }
                    )
                    center_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import tugadi: {region_count} viloyat, {district_count} tuman, {center_count} madaniyat markazi"
        ))
