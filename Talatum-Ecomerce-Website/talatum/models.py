from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ─── Category ────────────────────────────────────────────────────────────────
class Category(db.Model):
    __tablename__ = 'categories'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    slug        = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text)
    image       = db.Column(db.String(255))
    icon        = db.Column(db.String(100), default='fas fa-tag')
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    products    = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

# ─── Product ──────────────────────────────────────────────────────────────────
class Product(db.Model):
    __tablename__ = 'products'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(200), nullable=False)
    slug            = db.Column(db.String(220), nullable=False, unique=True)
    description     = db.Column(db.Text)
    short_desc      = db.Column(db.String(500))
    price           = db.Column(db.Float, nullable=False)
    sale_price      = db.Column(db.Float)
    stock           = db.Column(db.Integer, default=0)
    sku             = db.Column(db.String(100), unique=True)
    brand           = db.Column(db.String(100))
    weight          = db.Column(db.Float)
    is_active       = db.Column(db.Boolean, default=True)
    is_featured     = db.Column(db.Boolean, default=False)
    is_bestseller   = db.Column(db.Boolean, default=False)
    is_new_arrival  = db.Column(db.Boolean, default=False)
    is_flash_sale   = db.Column(db.Boolean, default=False)
    is_premium      = db.Column(db.Boolean, default=False)
    is_limited      = db.Column(db.Boolean, default=False)
    cod_available   = db.Column(db.Boolean, default=True)
    free_shipping   = db.Column(db.Boolean, default=False)
    views           = db.Column(db.Integer, default=0)
    category_id     = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images          = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    cart_items      = db.relationship('CartItem', backref='product', lazy='dynamic')
    order_items     = db.relationship('OrderItem', backref='product', lazy='dynamic')
    wishlist_items  = db.relationship('Wishlist', backref='product', lazy='dynamic')
    reviews         = db.relationship('Review', backref='product', lazy='dynamic')

    @property
    def main_image(self):
        img = self.images.filter_by(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img.image_url if img else 'default-product.jpg'

    @property
    def effective_price(self):
        return self.sale_price if self.sale_price else self.price

    @property
    def discount_percent(self):
        if self.sale_price and self.price > 0:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0

    @property
    def avg_rating(self):
        approved = self.reviews.filter_by(is_approved=True).all()
        if not approved:
            return 0
        return round(sum(r.rating for r in approved) / len(approved), 1)

    @property
    def review_count(self):
        return self.reviews.filter_by(is_approved=True).count()

    def __repr__(self):
        return f'<Product {self.name}>'

# ─── ProductImage ─────────────────────────────────────────────────────────────
class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url  = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    alt_text   = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── User ─────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(80), unique=True, nullable=False)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    password_hash   = db.Column(db.String(256), nullable=False)
    first_name      = db.Column(db.String(80))
    last_name       = db.Column(db.String(80))
    phone           = db.Column(db.String(20))
    avatar          = db.Column(db.String(255), default='default-avatar.png')
    is_active       = db.Column(db.Boolean, default=True)
    is_banned       = db.Column(db.Boolean, default=False)
    is_admin        = db.Column(db.Boolean, default=False)
    email_verified  = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    last_login      = db.Column(db.DateTime)

    cart            = db.relationship('Cart', backref='user', uselist=False, cascade='all, delete-orphan')
    orders          = db.relationship('Order', backref='user', lazy='dynamic')
    wishlist        = db.relationship('Wishlist', backref='user', lazy='dynamic')
    addresses       = db.relationship('Address', backref='user', lazy='dynamic')
    reviews         = db.relationship('Review', backref='user', lazy='dynamic')
    notifications   = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    def __repr__(self):
        return f'<User {self.username}>'

# ─── Address ──────────────────────────────────────────────────────────────────
class Address(db.Model):
    __tablename__ = 'addresses'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label       = db.Column(db.String(50), default='Home')
    full_name   = db.Column(db.String(150))
    phone       = db.Column(db.String(20))
    address1    = db.Column(db.String(255))
    address2    = db.Column(db.String(255))
    city        = db.Column(db.String(100))
    state       = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country     = db.Column(db.String(100), default='Pakistan')
    is_default  = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Cart ─────────────────────────────────────────────────────────────────────
class Cart(db.Model):
    __tablename__ = 'carts'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items      = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)

# ─── CartItem ─────────────────────────────────────────────────────────────────
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id         = db.Column(db.Integer, primary_key=True)
    cart_id    = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    variant    = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def subtotal(self):
        return self.product.effective_price * self.quantity

# ─── Order ────────────────────────────────────────────────────────────────────
class Order(db.Model):
    __tablename__ = 'orders'
    id              = db.Column(db.Integer, primary_key=True)
    order_number    = db.Column(db.String(50), unique=True, nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status          = db.Column(db.String(50), default='pending')
    # pending | confirmed | processing | shipped | out_for_delivery | delivered | cancelled | refunded
    payment_method  = db.Column(db.String(50), default='cod')
    payment_status  = db.Column(db.String(50), default='pending')
    subtotal        = db.Column(db.Float, default=0)
    shipping_cost   = db.Column(db.Float, default=0)
    tax             = db.Column(db.Float, default=0)
    discount        = db.Column(db.Float, default=0)
    total           = db.Column(db.Float, default=0)
    coupon_code     = db.Column(db.String(50))
    notes           = db.Column(db.Text)
    # Shipping address snapshot
    ship_name       = db.Column(db.String(150))
    ship_phone      = db.Column(db.String(20))
    ship_address1   = db.Column(db.String(255))
    ship_address2   = db.Column(db.String(255))
    ship_city       = db.Column(db.String(100))
    ship_state      = db.Column(db.String(100))
    ship_postal     = db.Column(db.String(20))
    ship_country    = db.Column(db.String(100))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items           = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    STATUS_LABELS = {
        'pending':           ('Pending',           'warning'),
        'confirmed':         ('Confirmed',          'info'),
        'processing':        ('Processing',         'primary'),
        'shipped':           ('Shipped',            'info'),
        'out_for_delivery':  ('Out for Delivery',   'primary'),
        'delivered':         ('Delivered',          'success'),
        'cancelled':         ('Cancelled',          'danger'),
        'refunded':          ('Refunded',           'secondary'),
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, ('Unknown', 'secondary'))

# ─── OrderItem ────────────────────────────────────────────────────────────────
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id           = db.Column(db.Integer, primary_key=True)
    order_id     = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id   = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200))
    product_img  = db.Column(db.String(255))
    quantity     = db.Column(db.Integer, default=1)
    price        = db.Column(db.Float)
    variant      = db.Column(db.String(100))

    @property
    def subtotal(self):
        return self.price * self.quantity

# ─── Wishlist ─────────────────────────────────────────────────────────────────
class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id'),)

# ─── Review ───────────────────────────────────────────────────────────────────
class Review(db.Model):
    __tablename__ = 'reviews'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating      = db.Column(db.Integer, nullable=False)
    title       = db.Column(db.String(200))
    body        = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Coupon ───────────────────────────────────────────────────────────────────
class Coupon(db.Model):
    __tablename__ = 'coupons'
    id              = db.Column(db.Integer, primary_key=True)
    code            = db.Column(db.String(50), unique=True, nullable=False)
    discount_type   = db.Column(db.String(20), default='percent')  # percent | fixed
    discount_value  = db.Column(db.Float, nullable=False)
    min_order       = db.Column(db.Float, default=0)
    max_uses        = db.Column(db.Integer, default=100)
    used_count      = db.Column(db.Integer, default=0)
    is_active       = db.Column(db.Boolean, default=True)
    expires_at      = db.Column(db.DateTime)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Notification ─────────────────────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.String(200))
    message    = db.Column(db.Text)
    type       = db.Column(db.String(50), default='info')  # info | success | warning | danger
    is_read    = db.Column(db.Boolean, default=False)
    link       = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Newsletter ───────────────────────────────────────────────────────────────
class Newsletter(db.Model):
    __tablename__ = 'newsletters'
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Banner ───────────────────────────────────────────────────────────────────
class Banner(db.Model):
    __tablename__ = 'banners'
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200))
    subtitle   = db.Column(db.String(300))
    image      = db.Column(db.String(255))
    link       = db.Column(db.String(255))
    is_active  = db.Column(db.Boolean, default=True)
    order      = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
