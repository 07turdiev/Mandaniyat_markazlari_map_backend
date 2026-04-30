import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from centers.views import passport_pdf
from centers.models import CulturalCenter

center = CulturalCenter.objects.first()
if center:
    factory = RequestFactory()
    request = factory.get(f'/api/centers/{center.id}/passport-pdf/')
    response = passport_pdf(request, center.id)
    if response.status_code == 200:
        with open('test_output.pdf', 'wb') as f:
            f.write(response.content)
        print("Success! Created test_output.pdf")
    else:
        print(f"Failed with status code: {response.status_code}")
else:
    print("No cultural centers found in DB.")
