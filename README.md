Flask E-Commerce Website

A modern full-stack E-Commerce web application built using Python Flask with a professional responsive UI and a powerful admin dashboard. The project provides a complete online shopping experience similar to Amazon, Daraz, Shopify, and Noon.

Features
Customer Features
User Registration & Login
Secure Authentication
Product Listings
Product Search & Filters
Product Detail Pages
Shopping Cart
Wishlist System
Checkout System
Order Tracking
Product Reviews & Ratings
Responsive Mobile-Friendly Design
Dark/Light Modern UI
Newsletter Subscription
Flash Sales & Featured Products
Admin Features
Secure Admin Dashboard
Product Management
Category Management
Order Management
User Management
Review Moderation
Inventory Tracking
Revenue Analytics
Sales Statistics
Low Stock Alerts
Technologies Used
Backend
Python
Flask
Flask SQLAlchemy
Flask Login
Flask WTF
SQLite
REST APIs
Frontend
HTML5
CSS3
Bootstrap 5
JavaScript
AJAX / Fetch API
Project Structure
talatum/
│
├── app.py
├── config.py
├── models.py
├── forms.py
├── README.md
├── .env
│
├── routes/
│   ├── admin.py
│   ├── api.py
│   └── user.py
│
├── templates/
│   ├── admin/
│   ├── errors/
│   ├── partials/
│   ├── user/
│   └── base.html
│
├── static/
│   ├── css/
│   ├── js/
│   │   └── main.js
│   ├── images/
│   └── uploads/
│       ├── avatars/
│       ├── banners/
│       ├── categories/
│       └── products/
│
└── instance/
Installation
Clone Repository
git clone https://github.com/Talatum-Ecomerce-Website/flask-ecommerce.git
cd flask-ecommerce
Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Mac/Linux
python3 -m venv venv
source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Configure Environment Variables

Create a .env file:

SECRET_KEY=your_secret_key
Database Setup
flask db init
flask db migrate
flask db upgrade
Run Project
python app.py

Open browser:

http://127.0.0.1:5000
Security Features
Password Hashing
CSRF Protection
Session Security
Input Validation
Secure Admin Routes
SQL Injection Prevention
XSS Protection
API Features
Product APIs
Cart APIs
Wishlist APIs
Order APIs
Search APIs
Future Improvements
Stripe Integration
PayPal Integration
AI Recommendations
Multi Vendor Support
Email Verification
Docker Deployment
PostgreSQL Support
Redis Caching
Screenshots

Add screenshots of:

Homepage
Product Page
Cart
Checkout
Admin Dashboard
License

This project is licensed under the MIT License.

Author

Developed by Husnain ALi and Fatima Aslam using Flask and Bootstrap 5.
