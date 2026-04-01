import time

from django.core.management.base import BaseCommand

from centers.models import CulturalCenter, Mahalla
from centers.translation import translate_batch


# Tarjima qilinadigan maydonlar: (model, [(manba_maydon, maqsad_maydon), ...])
TRANSLATABLE_FIELDS = [
    (CulturalCenter, [
        ("name", "name_ru"),
        ("balance_holder", "balance_holder_ru"),
        ("building_technical_info", "building_technical_info_ru"),
    ]),
    (Mahalla, [
        ("name", "name_ru"),
    ]),
]

BATCH_SIZE = 50


class Command(BaseCommand):
    help = "Tahrirchi API orqali o'zbekchadan ruschaga avtomatik tarjima"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Tarjimalarni ko'rsatadi, lekin bazaga saqlamaydi",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Mavjud tarjimalarni ham qayta tarjima qiladi",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN rejimi — bazaga yozilmaydi"))

        total_translated = 0

        for model, fields in TRANSLATABLE_FIELDS:
            model_name = model.__name__
            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"Model: {model_name}")
            self.stdout.write(f"{'='*50}")

            for source_field, target_field in fields:
                self.stdout.write(f"\n  {source_field} → {target_field}")

                # Tarjima kerak bo'lgan yozuvlarni topish
                filters = {
                    f"{source_field}__gt": "",  # manba bo'sh emas
                }
                if not force:
                    filters[target_field] = ""  # maqsad bo'sh

                queryset = model.objects.filter(**filters)
                count = queryset.count()

                if count == 0:
                    self.stdout.write(self.style.SUCCESS("  Barchasi tarjima qilingan!"))
                    continue

                self.stdout.write(f"  Tarjima kutayotgan: {count} ta yozuv")

                # Batchlarga bo'lib tarjima qilish
                for offset in range(0, count, BATCH_SIZE):
                    batch = queryset[offset:offset + BATCH_SIZE]
                    texts_with_ids = []

                    for obj in batch:
                        text = getattr(obj, source_field, "").strip()
                        if text:
                            texts_with_ids.append((obj.pk, text))

                    if not texts_with_ids:
                        continue

                    self.stdout.write(
                        f"  Batch {offset // BATCH_SIZE + 1}: "
                        f"{len(texts_with_ids)} ta matn tarjima qilinmoqda..."
                    )

                    translations = translate_batch(texts_with_ids)

                    if not translations:
                        self.stderr.write(self.style.ERROR("  Tarjima qaytmadi!"))
                        continue

                    for obj_id, translated in translations.items():
                        if dry_run:
                            original = dict(texts_with_ids).get(obj_id, "?")
                            self.stdout.write(f"    [{obj_id}] {original} → {translated}")
                        else:
                            model.objects.filter(pk=obj_id).update(
                                **{target_field: translated}
                            )

                    total_translated += len(translations)

                    # API limitiga tushmaslik uchun
                    time.sleep(0.5)

        self.stdout.write(f"\n{'='*50}")
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"Jami {total_translated} ta matn tarjima qilindi (DRY RUN)")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Jami {total_translated} ta matn tarjima qilib saqlandi!")
            )
