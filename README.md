# WESTINGEN

Backend odaklı bir iş başvurusu demosu. Çok kiracılı (B2B2C) yapıda sensör verisi toplama, saklama ve görselleştirme problemini çözer.

## What is WESTINGEN?

WESTINGEN is a minimal Flask-based application that demonstrates sensor data ingestion, storage, and visualization. It is designed as a job application demo to showcase backend development skills with Python and Flask.

## Tech Stack

- **Backend**: Python 3.8+, Flask 3.0
- **Database**: PostgreSQL 12+
- **Frontend**: Server-rendered HTML with Bootstrap 5 and Chart.js (via CDN)
- **Dependencies**: psycopg2-binary, requests, python-dotenv

## Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip

### Step-by-Step Setup

1. **Clone and navigate to the project**:
   ```bash
   cd westingen
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   ```bash
   createdb westingen
   psql westingen < migrations/001_init.sql
   psql westingen < migrations/002_b2b2c.sql
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and set your DATABASE_URL if different from default
   ```

6. **Seed demo data**:
   ```bash
   python scripts/seed_demo.py
   ```
   
   This creates:
   - Demo Company
   - Owner user: `owner@demo.com` / `demo1234`
   - Device: `robot-001` with API key
   
   **Note:** The script will print the device API key. Save it for data generation.

## Running the Application

### Start the Flask Server

```bash
python run.py
```

The application will be available at `http://localhost:5001`

**Note:** Port 5001 is used instead of 5000 because macOS reserves port 5000 for AirPlay.

- Login: `http://localhost:5001/login` (use credentials from seed script)
- Dashboard: `http://localhost:5001/` (requires login)
- Health check: `http://localhost:5001/api/health`

### Login Credentials

After running the seed script, use:
- **Email:** `owner@demo.com`
- **Password:** `demo1234`

### Generate Sample Data

In a separate terminal, run:

```bash
python scripts/generate_data.py --count 50 --rate 5 --device-key <API_KEY>
```

Replace `<API_KEY>` with the device API key printed by `seed_demo.py`.

Alternatively, set the `DEVICE_KEY` environment variable:
```bash
export DEVICE_KEY=<API_KEY>
python scripts/generate_data.py --count 50 --rate 5
```

This will generate sensor readings at the specified rate and send them to the API.

**Note:** Devices are simulated clients (scripts). The API is compatible with real devices, but this demo does not require hardware.

Options:
- `--count`: Number of readings to generate (default: 200)
- `--rate`: Readings per second (default: 5)
- `--device-key`: Device API key (required, or use DEVICE_KEY env var)
- `--url`: Base URL of the API (default: http://localhost:5001)

## API Endpoints

- `GET /api/health` - Health check endpoint (public)
- `POST /api/ingest` - Ingest sensor data (requires X-DEVICE-KEY header)
- `GET /api/latest?limit=50` - Get latest sensor readings (requires login, tenant-filtered)
- `GET /api/stats` - Get statistics about sensor readings (requires login, tenant-filtered)

### Example: Ingest Sensor Data

```bash
curl -X POST http://localhost:5001/api/ingest \
  -H "Content-Type: application/json" \
  -H "X-DEVICE-KEY: <YOUR_DEVICE_API_KEY>" \
  -d '{
    "temperature_c": 36.4,
    "accel_x": 0.12,
    "accel_y": -0.03,
    "accel_z": 9.81,
    "latitude": 39.92,
    "longitude": 32.85
  }'
```

**Note:** Replace `<YOUR_DEVICE_API_KEY>` with the API key from `seed_demo.py` or create a device via the admin panel (owner role required).

## Dashboard Features

The dashboard displays:
- **KPI Cards**: Total records, latest temperature, last update time
- **Temperature Chart**: Line chart showing temperature over time (auto-updates every 5 seconds)
- **Data Table**: Latest 50 sensor readings with all fields

## What is Intentionally Omitted

This is a demo application. The following are intentionally not included:

- Advanced authentication mechanisms (OAuth, JWT, SSO)
- Production-grade authorization policies
- Production hardening (HTTPS, rate limiting, etc.)
- Microservices architecture
- React or other SPA frameworks
- Docker containerization
- Unit tests
- CI/CD pipelines
- Device deletion (devices cannot be deleted to preserve historical data integrity)

These omissions are by design to keep the demo focused and runnable in under 5 minutes.

## Screenshots

### Dashboard Overview
![Dashboard Overview](screenshots/dashboard-overview.png)

### Temperature Chart
![Temperature Chart](screenshots/dashboard-chart.png)

### Latest Sensor Readings
![Latest Sensor Readings](screenshots/dashboard-table.png)

## Türkçe Açıklama

### WESTINGEN Nedir?

WESTINGEN, sensör verilerini toplayan, veritabanında saklayan ve web arayüzünde görselleştiren bir demo uygulamasıdır. Python ve Flask kullanılarak geliştirilmiştir.

### Özellikler

- **Çok kiracılı (Multi-tenant) yapı**: Şirketler kendi cihazlarını ve kullanıcılarını yönetir
- **Cihaz kimlik doğrulama**: Cihazlar API anahtarı ile veri gönderir
- **Kullanıcı girişi**: Oturum tabanlı kimlik doğrulama
- **Veri görselleştirme**: Dashboard'da grafikler ve tablolar
- **RESTful API**: Cihazlar ve kullanıcılar için API endpoint'leri

### Teknoloji Stack

- **Backend**: Python 3.8+, Flask 3.0
- **Veritabanı**: PostgreSQL 12+
- **Frontend**: Server-rendered HTML (Bootstrap 5, Chart.js)
- **Kimlik Doğrulama**: Flask sessions (kullanıcılar), API key (cihazlar)

### Kurulum

1. PostgreSQL veritabanı oluşturun
2. Migration dosyalarını çalıştırın
3. Demo verilerini seed edin
4. Uygulamayı başlatın

Detaylı kurulum adımları için yukarıdaki "Setup" bölümüne bakın.

### Demo Kullanım

1. `python scripts/seed_demo.py` çalıştırın (kullanıcı ve cihaz oluşturur)
2. `python run.py` ile sunucuyu başlatın
3. `http://localhost:5001/login` adresinden giriş yapın
4. Dashboard'da verileri görüntüleyin
5. `python scripts/generate_data.py` ile test verisi oluşturun

### İş Başvurusu İçin

Bu proje, backend geliştirme becerilerini göstermek için hazırlanmış bir demo uygulamasıdır. Üretim ortamı için tasarlanmamıştır.

## License

This is a demo project for job application purposes.
