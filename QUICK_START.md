# 🚀 Швидкий запуск Ukrainian Airlines

## ✅ Що вже запущено:

### Backend (Django API)
- **URL**: http://localhost:8000
- **Swagger документація**: http://localhost:8000/api/doc/swagger/
- **Статус**: 🟢 ПРАЦЮЄ

### Web Frontend
- **URL**: http://localhost:3000
- **Статус**: 🟢 ПРАЦЮЄ

### Android App
- **Проект**: `/android_app/`
- **Статус**: 📱 Готовий до збірки

---

## 🔧 Як запустити (якщо потрібно перезапустити)

### 1. Backend (Django)
```bash
cd /Users/user/Ukrainian-Airlines
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 2. Web Frontend
```bash
cd /Users/user/Ukrainian-Airlines/web_frontend
python3 -m http.server 3000
```

### 3. Android App
1. Відкрийте Android Studio
2. Оберіть "Open" -> `/Users/user/Ukrainian-Airlines/android_app/`
3. Дочекайтеся синхронізації Gradle
4. Натисніть "Run" або подивіться на емуляторі/пристрої

---

## 🧪 Тестування

### API Endpoints (працюють):
- `GET /api/airlines/airports/` - Список аеропортів ✅
- `GET /api/airlines/flights/` - Список рейсів ✅
- `GET /api/airlines/routes/` - Маршрути ✅
- `POST /api/airlines/get-ways/` - Пошук з пересадками ✅

### Web Frontend функції:
- ✅ Завантаження аеропортів з API
- ✅ Пошук прямих рейсів
- ✅ Пошук рейсів з пересадками
- ✅ Відображення результатів
- ✅ Responsive дизайн

### Тестові дані:
- 16 аеропортів (Київ, Львів, Харків, Одеса, Варшава, Прага, Лондон та ін.)
- 22+ рейси з різними маршрутами
- Тестові користувачі: `yaros` / `yaros_test` (пароль: `12345`)

---

## 📱 Android App конфігурація

### API URL налаштування:
- **Емулятор**: `http://10.0.2.2:8000/` ✅
- **Фізичний пристрій**: потрібно замінити на IP комп'ютера

### Як змінити API URL для фізичного пристрою:
1. Знайдіть IP вашого комп'ютера: `ifconfig | grep inet`
2. Відредагуйте файл:
   ```
   android_app/app/src/main/java/com/example/ukrainianairlines/data/api/UkrainianAirlinesApi.kt
   ```
3. Змініть BASE_URL на: `http://YOUR_IP:8000/`

---

## 🛠 Структура проекту

```
Ukrainian-Airlines/
├── 🔧 Backend (Django REST API)
│   ├── airlines_api/          # Основне API
│   ├── user/                  # Авторизація
│   ├── chat/                  # Чат (додатково)
│   └── db.sqlite3            # База даних з тестовими даними
│
├── 🌐 Web Frontend
│   └── web_frontend/index.html # Односторінковий додаток
│
├── 📱 Android App
│   └── android_app/           # Kotlin/Android проект
│
└── 📋 Документація
    ├── README.md             # Основна документація
    └── QUICK_START.md        # Цей файл
```

---

## 🎯 Наступні кроки для тестування:

1. **Web Frontend**: http://localhost:3000
   - Оберіть аеропорти відправлення/прибуття
   - Встановіть дату
   - Натисніть "Знайти рейси"

2. **API тестування**: http://localhost:8000/api/doc/swagger/
   - Подивіться всі доступні endpoints
   - Протестуйте різні запити

3. **Android App**:
   - Відкрийте в Android Studio
   - Запустіть на емуляторі
   - Протестуйте пошук та бронювання

---

## 🐛 Якщо щось не працює:

### Django не запускається:
```bash
pkill -f "python manage.py runserver"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
python manage.py runserver 0.0.0.0:8000
```

### Frontend не відповідає:
```bash
pkill -f "python3 -m http.server"
cd web_frontend && python3 -m http.server 3000
```

### Android не підключається до API:
- Перевірте що Django сервер працює на порту 8000
- Для емулятора URL має бути `http://10.0.2.2:8000/`
- Для пристрою - замініть на IP комп'ютера

---

## 💡 Фічі для демонстрації:

1. **Алгоритм Дейкстри** - пошук оптимальних маршрутів з пересадками
2. **JWT авторизація** - безпечна аутентифікація
3. **RESTful API** - правильна архітектура API
4. **Material Design 3** - сучасний Android UI
5. **Responsive Web** - адаптивний веб-інтерфейс
6. **Real-time search** - миттєвий пошук рейсів

Усе готово до тестування! 🎉