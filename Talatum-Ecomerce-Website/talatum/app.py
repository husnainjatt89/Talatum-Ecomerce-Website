import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db, User, Cart
from routes.user import user_bp
from routes.admin import admin_bp
from routes.api import api_bp

csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'categories'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)
    # Exempt API routes from CSRF
    csrf.exempt(api_bp)

    login_manager = LoginManager(app)
    login_manager.login_view = 'user.login'
    login_manager.login_message_category = 'warning'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Context processors
    @app.context_processor
    def inject_globals():
        from models import Category, Wishlist, Notification
        from flask_login import current_user
        categories = Category.query.filter_by(is_active=True).all()
        cart_count = 0
        wish_count = 0
        notif_count = 0
        if current_user.is_authenticated:
            cart = Cart.query.filter_by(user_id=current_user.id).first()
            cart_count = cart.item_count if cart else 0
            wish_count = Wishlist.query.filter_by(user_id=current_user.id).count()
            notif_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(
            nav_categories=categories,
            cart_count=cart_count,
            wish_count=wish_count,
            notif_count=notif_count,
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Template filters
    @app.template_filter('price')
    def price_filter(value):
        try:
            if value is None:
                return 'Rs.0'
            return f"Rs.{float(value):,.0f}"
        except (TypeError, ValueError):
            return str(value)

    @app.template_filter('stars')
    def stars_filter(rating):
        full  = int(rating)
        half  = 1 if (rating - full) >= 0.5 else 0
        empty = 5 - full - half
        return '★' * full + '½' * half + '☆' * empty

    with app.app_context():
        db.create_all()
        _seed_data(app)

    return app

def _seed_data(app):
    """Seed initial admin and sample data."""
    from models import User, Category, Product, ProductImage, Banner, Cart
    from utils import slugify

    # Admin user
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username='admin', email=app.config['ADMIN_EMAIL'],
            first_name='Admin', last_name='Talatum', is_admin=True, is_active=True
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()

    # Categories
    cats_data = [
        ('Exclusive Perfumery', 'fas fa-spray-can'),
        ('Designer Perfumery', 'fas fa-star'),
        ('Men Fashion', 'fas fa-male'),
        ('Women Fashion', 'fas fa-female'),
        ('Loafers', 'fas fa-shoe-prints'),
        ('Eye Wear', 'fas fa-glasses'),
        ('Tote Bags', 'fas fa-shopping-bag'),
        ('Personal Care', 'fas fa-heart'),
    ]
    for name, icon in cats_data:
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, slug=slugify(name), icon=icon)
            db.session.add(cat)
    db.session.commit()

    # Sample products
    if Product.query.count() == 0:
        cat_perf = Category.query.filter_by(name='Exclusive Perfumery').first()
        cat_men  = Category.query.filter_by(name='Men Fashion').first()
        sample_products = [
            {'name': 'Creed Millesime Wild Vetiver 100ML', 'price': 115900, 'brand': 'CREED',
             'is_featured': True, 'is_bestseller': True, 'cat': cat_perf},
            {'name': 'Memo Paris Portobello Road EDP 75ML', 'price': 83700, 'brand': 'MEMO PARIS',
             'is_featured': True, 'is_new_arrival': True, 'cat': cat_perf},
            {'name': 'Nishane Meant To Be Seen 100ML', 'price': 129900, 'brand': 'NISHANE',
             'is_bestseller': True, 'is_flash_sale': True, 'sale_price': 115000, 'cat': cat_perf},
            {'name': 'Xerjoff Black Moon Light Perfume 50ML', 'price': 107100, 'brand': 'XERJOFF',
             'is_featured': True, 'cat': cat_perf},
            {'name': 'Clive Christian Strange Heavens 50ML', 'price': 174900, 'brand': 'CLIVE CHRISTIAN',
             'is_premium': True, 'is_limited': True, 'cat': cat_perf},
            {'name': 'Clive Christian Iconic Feminine 50ML', 'price': 139900, 'brand': 'CLIVE CHRISTIAN',
             'is_premium': True, 'cat': cat_perf},
            {'name': 'Burberry Check Collar Sweatshirt', 'price': 300000, 'brand': 'BURBERRY',
             'is_bestseller': True, 'cat': cat_men},
            {'name': 'Fendi FF Metal Loafers Black Selleria', 'price': 361600, 'sale_price': 325350,
             'brand': 'FENDI', 'is_flash_sale': True, 'cat': cat_men},
        ]
        for sp in sample_products:
            cat = sp.pop('cat')
            if not cat:
                continue
            slug = slugify(sp['name'])
            base, counter = slug, 1
            while Product.query.filter_by(slug=slug).first():
                slug = f'{base}-{counter}'; counter += 1
            p = Product(
                name=sp['name'], slug=slug,
                description=f"Premium quality {sp['name']} from {sp.get('brand', 'Talatum')}. "
                            f"Experience luxury and elegance with every use.",
                short_desc=f"Authentic {sp.get('brand', '')} product.",
                price=sp['price'],
                sale_price=sp.get('sale_price'),
                stock=50, brand=sp.get('brand'),
                category_id=cat.id,
                is_featured=sp.get('is_featured', False),
                is_bestseller=sp.get('is_bestseller', False),
                is_new_arrival=sp.get('is_new_arrival', False),
                is_flash_sale=sp.get('is_flash_sale', False),
                is_premium=sp.get('is_premium', False),
                is_limited=sp.get('is_limited', False),
                cod_available=True, free_shipping=sp['price'] >= 100000,
            )
            db.session.add(p)
        db.session.commit()

    # Default banner
    if Banner.query.count() == 0:
        b = Banner(title='Introducing Wild Vetiver', subtitle='Experience the finest luxury fragrances',
                   link='/products', order=0, is_active=True)
        db.session.add(b)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
