# सेवासेतु — SevaSetu
### Maharashtra's Own Home Services Platform
> **"सेवा आणि विश्वास"** — Service & Trust

SevaSetu connects homeowners across Maharashtra with verified local service professionals. Built voice-first and multilingual for Tier-1, Tier-2, and Tier-3 cities.

---

## Login Credentials

### Admin
| Username | Password | URL |
|----------|----------|-----|
| `admin` | `admin@123` | `/admin/` |

### Demo Customers — Password: `demo@123`
| Username | Full Name | Phone |
|----------|-----------|-------|
| `customer_priya` | Priya Desai | +919123456780 |
| `customer_anita` | Anita Kulkarni | +919123456781 |
| `customer_sunita` | Sunita Sharma | +919123456782 |
| `customer_meena` | Meena Pawar | +919123456783 |
| `customer_kavita` | Kavita Joshi | +919123456784 |

### Demo Vendors — Password: `demo@123` (all verified ✓)
| Username | Full Name | Phone |
|----------|-----------|-------|
| `vendor_suresh` | Suresh Patil | +919876543210 |
| `vendor_ramesh` | Ramesh Jadhav | +919876543211 |
| `vendor_ganesh` | Ganesh Shinde | +919876543212 |
| `vendor_mahesh` | Mahesh More | +919876543213 |
| `vendor_rajesh` | Rajesh Bhosale | +919876543214 |
| `vendor_dinesh` | Dinesh Kulkarni | +919876543215 |
| `vendor_santosh` | Santosh Gaikwad | +919876543216 |
| `vendor_prakash` | Prakash Mane | +919876543217 |
| `vendor_vijay` | Vijay Kale | +919876543218 |
| `vendor_anil` | Anil Deshmukh | +919876543219 |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install razorpay  # for payments

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Seed data (run in order)
python manage.py seed_maharashtra     # 10 districts, 31 cities, 98 areas
python manage.py seed_services        # 7 categories, 29 service problems
python manage.py seed_subscriptions   # 5 subscription plans
python manage.py seed_demo            # 5 customers, 10 vendors, 20 bookings
python manage.py createsuperuser      # use: admin / admin@123

# 4. Start server
python manage.py runserver
```

For real-time chat & async tasks:
```bash
redis-server                              # Start Redis
celery -A sevasetu worker -l info         # Celery worker (separate terminal)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x, Python 3.10+ |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Real-time | Django Channels 4.x + Redis |
| Task Queue | Celery + Redis |
| Frontend | Tailwind CSS (CDN), Vanilla JS |
| AI Voice | Groq API — LLaMA 4 Scout |
| Payments | Razorpay (test mode) |
| Email | Gmail SMTP |
| PDF | WeasyPrint |
| Static Files | WhiteNoise |

---

## Project Structure

```
sevasetu/
├── accounts/          # User auth, roles, profiles (Customer/Vendor/Admin)
├── locations/         # District → City → Area (Maharashtra hierarchy)
├── services/          # ServiceCategory, ServiceProblem, SparePartEstimate
├── bookings/          # Booking lifecycle, payments, reviews, complaints
├── chat/              # Real-time WebSocket chat (Django Channels)
├── subscriptions/     # Subscription plans & user subscriptions
├── sevasathi/         # AI voice booking (Groq/LLaMA integration)
├── invoices/          # PDF invoice generation (WeasyPrint)
├── notifications/     # Celery-powered async notifications
├── dashboard/         # Customer, Vendor & Admin dashboards
├── templates/         # 35+ HTML templates (Tailwind CSS)
├── static/            # JS (voice, location, chat, tracking), CSS
└── locale/            # i18n: Marathi (mr), Hindi (hi), English (en)
```

---

## Services Catalogue (29 problems across 7 categories)

| # | Category | Services |
|---|----------|----------|
| 1 | 🔧 Plumbing | Tap leaking · Drain blocked · Geyser · Flush · New tap · Pipe leaking |
| 2 | ⚡ Electrical | Fan · Switch · Short circuit · Light fitting · MCB tripping |
| 3 | ❄️ AC & Appliances | AC not cooling · AC water leak · Washing machine · Fridge · Microwave |
| 4 | 🧹 Cleaning | Full home · Bathroom · Kitchen · Sofa cleaning |
| 5 | 🎨 Painting | Interior painting · Wall repair · Waterproofing |
| 6 | 🪚 Carpentry | Door repair · Furniture assembly · Window repair |
| 7 | 🐛 Pest Control | Cockroach · Mosquito · Termite treatment |

---

## Key Unique Features

### 🎤 SevaSathi — AI Voice Booking
Speak your problem in Marathi, Hindi, or English. Groq's LLaMA 4 Scout parses the intent and matches it to the right service — no typing needed.

### 🌐 Trilingual First
Every page, every service, every notification supports Marathi / Hindi / English. Users pick their preferred language at registration.

### 🔒 7-Day Service Guarantee
Customers can raise a complaint or guarantee claim within 7 days of service completion. Tracked via the Complaint model with automatic booking status change to DISPUTED.

### 👥 Same Professional Feature
Customers can request the same vendor who served them before for the same service category — building trust and continuity.

### 💬 Real-time Chat
Customer ↔ Vendor chat opens automatically when a vendor is assigned. Powered by Django Channels WebSocket at `ws/chat/<booking_id>/`.

### 💳 Razorpay Online Payments
Full Razorpay checkout integration with server-side HMAC signature verification. Booking is created first, then payment is collected via modal.

### 📄 Auto PDF Invoices
Invoices are auto-generated (WeasyPrint) when a customer confirms work completion. Stored in `media/invoices/`.

### 🔔 Smart Reminders
Celery tasks send seasonal maintenance reminders (e.g., AC service before summer, pest control before monsoon).

### 📦 Subscription Plans
5 pre-loaded plans: Monthly AC Maintenance, Weekly Home Cleaning, Monthly Pest Control, Quarterly Plumbing, Annual Home Care — with visit tracking.

### 👜 Vendor Wallet
80% of each booking's total price is automatically credited to the vendor's wallet upon booking closure.

---

## Booking Lifecycle (11 Stages)

```
REQUESTED → VENDOR_ASSIGNED → VENDOR_ACCEPTED → VENDOR_EN_ROUTE
→ IN_PROGRESS → WORK_COMPLETED → CUSTOMER_CONFIRMED
→ INVOICE_GENERATED → CLOSED
                    ↘ CANCELLED
                    ↘ DISPUTED
```

---

## Environment Variables (`.env`)

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=your-groq-api-key
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your-secret
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FIELD_ENCRYPTION_KEY=your-base64-encryption-key
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/locations/districts/` | List all districts |
| GET | `/api/locations/cities/?district_id=X` | Cities by district |
| GET | `/api/locations/areas/?city_id=X` | Areas by city |
| POST | `/sevasathi/api/process/` | Voice intent processing (Groq AI) |
| GET | `/bookings/api/<id>/status/` | Booking status + ETA JSON |
| POST | `/bookings/<id>/payment/create/` | Create Razorpay order |
| POST | `/bookings/<id>/payment/verify/` | Verify Razorpay payment |
| WS | `ws/chat/<booking_id>/` | WebSocket chat channel |

---

## Maharashtra Coverage

**10 Districts:** Pune, Mumbai Suburban, Thane, Nashik, Aurangabad, Nagpur, Solapur, Kolhapur, Satara, Ahmednagar

**31 Cities** including Pune, Mumbai, Thane, Nashik, Aurangabad, Nagpur, Solapur, Kolhapur, Satara, Ahmednagar, Navi Mumbai, Pimpri-Chinchwad and more.

**98 Areas** across all cities.

---

Built with ❤️ for Maharashtra | `demo@123` for all test accounts
