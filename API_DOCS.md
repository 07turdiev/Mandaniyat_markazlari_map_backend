# Madaniyat markazlari API — Frontend uchun

**Base URL:** `https://markaz.madaniyhayot.uz/api/`  
**Swagger UI:** `https://markaz.madaniyhayot.uz/api/docs/`

## Ko'p tilli qo'llab-quvvatlash

Barcha endpointlarda `Accept-Language` headeri orqali til tanlanadi:

```js
fetch('/api/map-data/', {
  headers: { 'Accept-Language': 'uz' } // uz | ru | en
})
```

---

## 1. Xarita ma'lumotlari (asosiy endpoint)

```
GET /api/map-data/
```

Frontendga kerakli barcha ma'lumotni bitta so'rovda qaytaradi.

**Javob:**
```json
{
  "regions": [
    {
      "soato": "1703",
      "name": "Andijon viloyati",
      "population": 3235100,
      "center": [40.78, 72.34],
      "districts": [
        {
          "soato": "1703202",
          "name": "Алтынкульский район",
          "population": 226700,
          "centers": [
            {
              "id": 1,
              "name": "Markaz nomi",
              "category": "vazirlik",
              "balance_holder": "Andijon shahar madaniyat bo'limi",
              "has_own_building": true,
              "activity_types": ["Madaniyat markazlari", "San'at yo'nalishi"],
              "lat": 40.78,
              "lng": 72.34,
              "address": "Navoiy ko'chasi 15",
              "map_url": "https://maps.google.com/...",
              "image": "/media/centers/photo.jpg",

              "circles_count": 5,
              "titled_teams_count": 2,
              "library_activity_count": 1,

              "management_staff": 1.75,
              "creative_staff": 10,
              "technical_staff": 3,
              "titled_team_staff": 5,
              "total_employees": 19,

              "total_land_area": 0.5,
              "building_area": 1200.0,
              "buildings_count": 2,
              "built_year": 1985,
              "building_floors": 2,
              "condition": "Yaxshi",
              "building_technical_info": "G'isht bino",
              "rooms_count": 15,
              "auditorium_area": 200.0,
              "dining_area": 50.0,
              "restrooms_count": 4,
              "additional_buildings_count": 1,

              "has_heating": true,
              "has_electricity": true,
              "has_gas": true,
              "has_water": true,
              "has_sewerage": true,

              "serving_mahallas": [
                {"id": 124, "name": "Navbahor", "tin": "207140195"}
              ],
              "mahalla_id": "207140195",
              "mahalla_name": "Guliston",
              "mahalla_population": 5000
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 2. Statistika

```
GET /api/statistics/
```

**Javob:**
```json
{
  "total_centers": 245,
  "total_regions": 14,
  "total_districts": 206,
  "total_population": 36024900,
  "by_category": {
    "vazirlik": 50,
    "hokimlik": 120,
    "dxsh": 45,
    "sotiladi": 30
  },
  "by_condition": {
    "Yaxshi": 100,
    "O'rtacha": 80,
    "Yomon": 40,
    "Tamir talab": 25
  }
}
```

---

## 3. Viloyatlar

```
GET /api/regions/              # Ro'yxat (soato, name, population, center, district_count, center_count)
GET /api/regions/{slug}/       # Tafsilot (tumanlar va markazlar bilan)
```

---

## 4. Tumanlar

```
GET /api/districts/            # Ro'yxat
GET /api/districts/?region={slug}  # Viloyat bo'yicha filtrlash
GET /api/districts/{slug}/     # Tafsilot (markazlar bilan)
```

---

## 5. Mahallalar

```
GET /api/mahallas/                    # Ro'yxat
GET /api/mahallas/?district={soato}   # Tuman SOATO bo'yicha
GET /api/mahallas/?region={soato}     # Viloyat SOATO bo'yicha
GET /api/mahallas/{id}/               # Tafsilot
```

---

## 6. Madaniyat markazlari

```
GET /api/centers/                          # Ro'yxat
GET /api/centers/?region={slug}            # Viloyat bo'yicha
GET /api/centers/?district={slug}          # Tuman bo'yicha
GET /api/centers/?category={category}      # Kategoriya bo'yicha
GET /api/centers/{id}/                     # Tafsilot (rasmlar, mahallalar bilan)
```

---

## Maydonlar lug'ati

### Kategoriyalar (`category`)
| Qiymat | Ma'nosi |
|--------|---------|
| `vazirlik` | Vazirlik |
| `hokimlik` | Hokimlik |
| `dxsh` | DXSh |
| `tugatiladi` | Tugatiladi |

### Bino holati (`condition`)
| Qiymat | Ma'nosi |
|--------|---------|
| `Yaxshi` | Yaxshi |
| `O'rtacha` | O'rtacha |
| `Avariya holatida` | Avariya holatida |
| `Tamir talab` | Tamir talab |

### Boolean maydonlar
| Maydon | Ma'nosi |
|--------|---------|
| `has_own_building` | O'z binosiga ega |
| `has_heating` | Isitish tizimi |
| `has_electricity` | Elektr-energiya |
| `has_gas` | Gaz |
| `has_water` | Ichimlik suvi |
| `has_sewerage` | Kanalizatsiya |

---

## Frontend misol (Vue/JS)

```js
const API = '/api'

// Xarita uchun barcha ma'lumot
const { regions } = await fetch(`${API}/map-data/`).then(r => r.json())

// Statistika
const stats = await fetch(`${API}/statistics/`).then(r => r.json())

// Ruscha
const data = await fetch(`${API}/map-data/`, {
  headers: { 'Accept-Language': 'ru' }
}).then(r => r.json())

// Filtrlash
const centers = await fetch(`${API}/centers/?region=andijon&category=vazirlik`)
  .then(r => r.json())
```
