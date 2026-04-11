# Madaniyat markazlari API — Frontend uchun

**Base URL:** `https://markaz.madaniyhayot.uz/api/`  
**Swagger UI:** `https://markaz.madaniyhayot.uz/api/docs/`  
**ReDoc:** `https://markaz.madaniyhayot.uz/api/redoc/`

---

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
          "name": "Oltinko'l tumani",
          "population": 226700,
          "centers": [
            {
              "id": 1,
              "name": "Markaz nomi",
              "category": "vazirlik",
              "is_featured": false,
              "balance_holder": "Andijon shahar madaniyat bo'limi",
              "has_own_building": true,
              "activity_types": ["Madaniyat markazlari", "Madaniyat va san'at yo'nalishi"],
              "lat": 40.78,
              "lng": 72.34,
              "map_url": "https://www.google.com/maps?q=40.78,72.34",

              "circles_count": 5,
              "titled_teams_count": 2,
              "library_activity_count": 1,

              "management_staff": 1.75,
              "creative_staff": 10.0,
              "technical_staff": 3.0,
              "titled_team_staff": 5.0,
              "total_employees": 19.75,

              "total_land_area": 0.5,
              "building_area": 1200.0,
              "buildings_count": 2,
              "built_year": 1985,
              "building_floors": 2,
              "condition": "Yaxshi",
              "building_technical_info": "G'isht bino",
              "rooms_count": 15,
              "auditorium_seats": 200,
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
  "total_mahallas": 9500,
  "total_population": 36024900,
  "by_category": {
    "vazirlik": 50,
    "hokimlik": 120,
    "dxsh": 45,
    "tugatiladi": 30
  },
  "by_condition": {
    "Yaxshi": 100,
    "O'rtacha": 80,
    "Avariya holatida": 40,
    "Tamir talab": 25
  }
}
```

---

## 3. Viloyatlar

### Ro'yxat
```
GET /api/regions/
```

**Javob:**
```json
{
  "count": 14,
  "results": [
    {
      "id": 1,
      "slug": "andijon",
      "name": "Andijon viloyati",
      "soato": "1703",
      "population": 3235100,
      "center": [40.78, 72.34],
      "district_count": 16,
      "center_count": 18,
      "mahalla_count": 750
    }
  ]
}
```

### Tafsilot
```
GET /api/regions/{slug}/
```

Tumanlar va ularning markazlari bilan to'liq ma'lumot qaytaradi.

---

## 4. Tumanlar

### Ro'yxat
```
GET /api/districts/
GET /api/districts/?region={slug}
```

**Javob:**
```json
{
  "count": 206,
  "results": [
    {
      "id": 1,
      "slug": "oltinkol",
      "name": "Oltinko'l tumani",
      "soato": "1703202",
      "population": 226700,
      "center_count": 3,
      "mahalla_count": 42
    }
  ]
}
```

### Tafsilot
```
GET /api/districts/{slug}/
```

Tumanga tegishli barcha markazlar bilan qaytaradi.

---

## 5. Mahallalar

```
GET /api/mahallas/                    # Barcha mahallalar
GET /api/mahallas/?district={soato}   # Tuman SOATO kodi bo'yicha
GET /api/mahallas/?region={soato}     # Viloyat SOATO kodi bo'yicha
GET /api/mahallas/{id}/               # Tafsilot
```

**Javob:**
```json
{
  "count": 9500,
  "results": [
    {
      "id": 1,
      "name": "Guliston MFY",
      "tin": "207140195",
      "soato": "1703202001",
      "code": "001",
      "population": 5000
    }
  ]
}
```

---

## 6. Madaniyat markazlari

### Ro'yxat
```
GET /api/centers/
GET /api/centers/?region={slug}
GET /api/centers/?district={slug}
GET /api/centers/?category={category}
```

Filtrlar bir-biri bilan kombinatsiya qilinishi mumkin:
```
GET /api/centers/?region=andijon&category=vazirlik
```

### Tafsilot
```
GET /api/centers/{id}/
```

**Javob:**
```json
{
  "id": 1,
  "name": "Madaniyat markazi nomi",
  "category": "vazirlik",
  "is_featured": false,
  "balance_holder": "Andijon shahar madaniyat bo'limi",
  "activity_types": [
    {"id": 1, "name": "Madaniyat markazlari"}
  ],
  "lat": 40.78,
  "lng": 72.34,
  "map_url": "https://www.google.com/maps?q=40.78,72.34",
  "has_own_building": true,

  "images": [
    {
      "id": 1,
      "image": "/media/centers/gallery/photo.jpg",
      "caption": "Bosh bino",
      "order": 1
    }
  ],
  "projects": [
    {
      "id": 1,
      "title": "Yangi sahna loyihasi",
      "media_type": "image",
      "file": "/media/centers/projects/loyiha.jpg",
      "caption": "Sahna rekonstruksiyasi",
      "order": 1
    },
    {
      "id": 2,
      "title": "Konsert videosi",
      "media_type": "video",
      "file": "/media/centers/projects/konsert.mp4",
      "caption": "2024 yilgi konsert",
      "order": 2
    }
  ],

  "circles_count": 5,
  "titled_teams_count": 2,
  "library_activity_count": 1,

  "management_staff": 1.75,
  "creative_staff": 10.0,
  "technical_staff": 3.0,
  "titled_team_staff": 5.0,
  "total_employees": 19.75,

  "total_land_area": 0.5,
  "building_area": 1200.0,
  "buildings_count": 2,
  "built_year": 1985,
  "building_floors": 2,
  "condition": "Yaxshi",
  "building_technical_info": "G'isht bino",
  "rooms_count": 15,
  "auditorium_seats": 200,
  "dining_area": 50.0,
  "restrooms_count": 4,
  "additional_buildings_count": 1,

  "has_heating": true,
  "has_electricity": true,
  "has_gas": true,
  "has_water": true,
  "has_sewerage": true,

  "mahalla": 1,
  "mahalla_name": "Guliston MFY",
  "mahalla_population": 5000,
  "serving_mahallas": [
    {"id": 124, "name": "Navbahor", "tin": "207140195", "soato": "1703202001", "code": "001", "population": 3000}
  ],
  "region_soato": "1703",
  "region_name": "Andijon viloyati",
  "district_soato": "1703202",
  "district_name": "Oltinko'l tumani"
}
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

### Loyiha turi (`media_type`)
| Qiymat | Ma'nosi |
|--------|---------|
| `image` | Rasm |
| `video` | Video |

### Boolean maydonlar
| Maydon | Ma'nosi |
|--------|---------|
| `is_featured` | Ajratilgan markaz (xaritada alohida ko'rsatiladi) |
| `has_own_building` | O'z binosiga ega |
| `has_heating` | Isitish tizimi |
| `has_electricity` | Elektr-energiya |
| `has_gas` | Gaz |
| `has_water` | Ichimlik suvi |
| `has_sewerage` | Kanalizatsiya |

### xadimlar (float — shtat birligi)
| Maydon | Ma'nosi |
|--------|---------|
| `management_staff` | Boshqaruv shtat birligi |
| `creative_staff` | Ijodiy xadimlar |
| `technical_staff` | Texnik xodimlar |
| `titled_team_staff` | Unvonga ega jamoalar xodimlari |
| `total_employees` | Jami (computed) |

---

## Pagination

Barcha ro'yxat endpointlari sahifalangan (50 ta per sahifa):

```json
{
  "count": 245,
  "next": "https://markaz.madaniyhayot.uz/api/centers/?page=2",
  "previous": null,
  "results": [...]
}
```

Sahifa o'zgartirish: `?page=2`, `?page=3` ...

---

## Frontend misol (Vue/JS)

```js
const API = '/api'

// Xarita uchun barcha ma'lumot
const { regions } = await fetch(`${API}/map-data/`).then(r => r.json())

// Statistika (umumiy, viloyat, tuman kesimida mahallalar soni bilan)
const stats = await fetch(`${API}/statistics/`).then(r => r.json())
// stats.total_mahallas — umumiy mahallalar soni

// Viloyatlar (har birida mahalla_count bor)
const { results: regions } = await fetch(`${API}/regions/`).then(r => r.json())

// Tumanlar (har birida mahalla_count bor)
const { results: districts } = await fetch(`${API}/districts/?region=andijon`).then(r => r.json())

// Ruscha
const data = await fetch(`${API}/map-data/`, {
  headers: { 'Accept-Language': 'ru' }
}).then(r => r.json())

// Filtrlash
const { results: centers } = await fetch(`${API}/centers/?region=andijon&category=vazirlik`)
  .then(r => r.json())

// Bitta markaz tafsiloti (rasmlar, loyihalar, mahallalar bilan)
const center = await fetch(`${API}/centers/1/`).then(r => r.json())
// center.projects — loyihalar (rasm + video)
// center.images — rasmlar galereyasi
// center.is_featured — ajratilgan markaz
```
