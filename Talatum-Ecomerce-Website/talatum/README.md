# تلاطم — Talatum E-Commerce Platform

**Her Nefeste Zarafet** — Elegance in Every Breath

A complete, production-ready Flask e-commerce platform for exclusive perfumery & fashion.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Edit `.env` with your settings (already pre-configured for development).

### 3. Run the app
```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

---

## 🔐 Default Credentials

| Role  | Email                  | Password   |
|-------|------------------------|------------|
| Admin | admin@talatum.com      | Admin@123  |

Admin panel: **http://127.0.0.1:5000/admin**

---

## 📁 Project Structure

```
talatum/
├── app.py              # App factory & entry point
├── config.py           # Configuration classes
├── models.py           # SQLAlchemy database models
├── forms.py            # WTForms form classes
├── utils.py            # Helper utilities
├── requirements.txt
├── .env                # Environment variables
├── routes/
│   ├── user.py         # Customer-facing routes
│   ├── admin.py        # Admin panel routes
│   └── api.py          # REST API endpoints
├── templates/
│   ├── base.html       # Base layout
│   ├── user/           # Customer pages
│   ├── admin/          # Admin pages
│   ├── partials/       # Reusable components
│   └── errors/         # Error pages
└── static/
    ├── css/main.css    # Main stylesheet
    ├── css/admin.css   # Admin stylesheet
    ├── js/main.js      # Main JavaScript
    ├── images/         # Static images
    └── uploads/        # User-uploaded files
```

---

## ✨ Features

### Customer Side
- 🏠 Rich homepage with hero slider, flash sale countdown, product sections
- 🔍 Live search with AJAX suggestions
- 🛍️ Product listing with filters, sorting, pagination
- 📦 Product detail with image gallery, reviews, related products
- 🛒 Shopping cart with quantity control & coupon system
- 💳 Checkout with COD, Card, PayPal options
- 📋 Order tracking with status timeline
- ❤️ Wishlist management
- 👤 User dashboard with profile, addresses, notifications
- 🌙 Dark / Light mode toggle

### Admin Panel (`/admin`)
- 📊 Dashboard with sales charts & analytics
- 📦 Full product CRUD with multi-image upload
- 🏷️ Category management
- 📋 Order management with status updates
- 👥 User management (ban/unban)
- ⭐ Review moderation
- 🎟️ Coupon system
- 🖼️ Banner management
- 📧 Newsletter subscribers
- 📥 CSV export

### API Endpoints
- `GET /api/products` — Product list
- `GET /api/products/<id>` — Product detail
- `GET /api/search/suggestions?q=` — Live search
- `GET /api/cart` — Cart contents
- `POST /api/cart/add` — Add to cart
- `GET /api/categories` — All categories

---

## 🛠️ Tech Stack

- **Backend**: Python Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: SQLite (easily swappable to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, Font Awesome 6, Vanilla JS
- **Security**: CSRF protection, password hashing, SQL injection prevention

---

## 🎨 Brand Colors

| Color | Hex       |
|-------|-----------|
| Gold  | `#c9a84c` |
| Dark  | `#0a0a0a` |
| Light | `#f8f6f0` |
