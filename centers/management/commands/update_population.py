"""
stat.uz dagi XML fayldan aholi sonini tumanlar va viloyatlar kesimida yangilaydi.
Ma'lumot manbasi: https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_246.xml

XML dagi har bir <series> elementida:
  - code="SOATO_KODI" (masalan: "1735401" - Nukus shahri)
  - <value time="2025">344.7</value> - 2025 yil aholi soni (ming kishida)

Foydalanish:
    python manage.py update_population
    python manage.py update_population --year 2024
    python manage.py update_population --dry-run
"""
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError

from django.core.management.base import BaseCommand
from centers.models import Region, District


STAT_UZ_XML_URL = 'https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_246.xml'


class Command(BaseCommand):
    help = "stat.uz dan aholi soni ma'lumotlarini yuklab, viloyat va tumanlar uchun yangilaydi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--year', type=str, default='2025',
            help="Qaysi yil uchun ma'lumot olish (default: 2025)"
        )
        parser.add_argument(
            '--url', type=str, default=STAT_UZ_XML_URL,
            help="XML fayl URL manzili"
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Faqat ko'rsatish, bazaga yozmay"
        )

    def handle(self, *args, **options):
        year = options['year']
        url = options['url']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN rejimi — bazaga yozilmaydi"))

        # 1. XML ni yuklab olish
        self.stdout.write(f"XML yuklanmoqda: {url}")
        try:
            with urlopen(url, timeout=30) as response:
                xml_data = response.read()
        except URLError as e:
            self.stderr.write(self.style.ERROR(f"XML yuklashda xatolik: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("XML muvaffaqiyatli yuklandi"))

        # 2. XML ni parse qilish
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            self.stderr.write(self.style.ERROR(f"XML parse xatolik: {e}"))
            return

        # 3. <data> ichidagi <series> elementlardan SOATO va aholi sonini olish
        data_element = root.find('data')
        if data_element is None:
            self.stderr.write(self.style.ERROR("XML da <data> elementi topilmadi"))
            return

        population_map = {}  # soato_code -> population (ming kishi)

        for series in data_element.findall('series'):
            code = series.get('code', '')
            if not code:
                continue

            # Kerakli yil uchun qiymatni topish
            for value_elem in series.findall('value'):
                if value_elem.get('time') == year:
                    try:
                        pop_thousands = float(value_elem.text)
                        # ming kishidan haqiqiy songa o'tkazish (344.7 -> 344700)
                        population_map[code] = int(pop_thousands * 1000)
                    except (ValueError, TypeError):
                        self.stderr.write(f"  Noto'g'ri qiymat: code={code}, value={value_elem.text}")
                    break

        self.stdout.write(f"XMLdan {len(population_map)} ta hudud uchun {year}-yil aholi soni topildi")

        # 4. Viloyatlarni yangilash
        region_updated = 0
        region_not_found = 0

        regions = Region.objects.all()
        for region in regions:
            if not region.soato:
                continue
            pop = population_map.get(region.soato)
            if pop is not None:
                old_pop = region.population
                if not dry_run:
                    region.population = pop
                    region.save(update_fields=['population'])
                region_updated += 1
                self.stdout.write(
                    f"  ✅ Viloyat: {region.name} (SOATO: {region.soato}) "
                    f"— {old_pop:,} → {pop:,}"
                )
            else:
                region_not_found += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  Viloyat topilmadi XMLda: {region.name} (SOATO: {region.soato})"
                    )
                )

        # 5. Tumanlarni yangilash
        district_updated = 0
        district_not_found = 0

        districts = District.objects.select_related('region').all()
        for district in districts:
            if not district.soato:
                continue
            pop = population_map.get(district.soato)
            if pop is not None:
                old_pop = district.population
                if not dry_run:
                    district.population = pop
                    district.save(update_fields=['population'])
                district_updated += 1
                self.stdout.write(
                    f"  ✅ Tuman: {district.name} (SOATO: {district.soato}) "
                    f"— {old_pop:,} → {pop:,}"
                )
            else:
                district_not_found += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  Tuman topilmadi XMLda: {district.name} (SOATO: {district.soato})"
                    )
                )

        # 6. Natija
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f"Natija ({year}-yil):\n"
            f"  Viloyatlar: {region_updated} yangilandi, {region_not_found} topilmadi\n"
            f"  Tumanlar:   {district_updated} yangilandi, {district_not_found} topilmadi"
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN — bazaga hech narsa yozilmadi!"))
