from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, abort, send_file)
from flask_login import login_required, current_user
from functools import wraps
from models import (db, User, Product, ProductImage, Category, Order, OrderItem,
                    Review, Coupon, Newsletter, Banner, Notification, Wishlist, Cart)
from forms import ProductForm, CategoryForm, CouponForm
from utils import save_image, slugify
from datetime import datetime, timedelta
from sqlalchemy import func
import io, csv

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return login_required(decorated)

# ─── Dashboard ────────────────────────────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    total_users    = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    total_orders   = Order.query.count()
    total_revenue  = db.session.query(func.sum(Order.total)).filter(Order.status == 'delivered').scalar() or 0
    recent_orders  = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock      = Product.query.filter(Product.stock <= 5, Product.is_active == True).all()
    pending_reviews = Review.query.filter_by(is_approved=False).count()
    # Sales last 7 days
    sales_data = []
    for i in range(6, -1, -1):
        day   = datetime.utcnow() - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0)
        end   = day.replace(hour=23, minute=59, second=59)
        rev   = db.session.query(func.sum(Order.total)).filter(
            Order.created_at.between(start, end)).scalar() or 0
        sales_data.append({'date': day.strftime('%b %d'), 'revenue': float(rev)})
    # Order status breakdown
    status_counts = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    return render_template('admin/dashboard.html',
        total_users=total_users, total_products=total_products,
        total_orders=total_orders, total_revenue=total_revenue,
        recent_orders=recent_orders, low_stock=low_stock,
        pending_reviews=pending_reviews, sales_data=sales_data,
        status_counts=dict(status_counts))

# ─── Products ─────────────────────────────────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def products():
    page     = request.args.get('page', 1, type=int)
    q        = request.args.get('q', '')
    query    = Product.query
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/products.html', products=products.items, pagination=products, q=q)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        # Ensure unique slug
        base, counter = slug, 1
        while Product.query.filter_by(slug=slug).first():
            slug = f'{base}-{counter}'; counter += 1
        product = Product(
            name=form.name.data, slug=slug,
            description=form.description.data, short_desc=form.short_desc.data,
            price=form.price.data, sale_price=form.sale_price.data or None,
            stock=form.stock.data, sku=form.sku.data, brand=form.brand.data,
            category_id=form.category_id.data,
            is_featured=form.is_featured.data, is_bestseller=form.is_bestseller.data,
            is_new_arrival=form.is_new_arrival.data, is_flash_sale=form.is_flash_sale.data,
            is_premium=form.is_premium.data, is_limited=form.is_limited.data,
            cod_available=form.cod_available.data, free_shipping=form.free_shipping.data,
        )
        db.session.add(product)
        db.session.flush()
        files = request.files.getlist('images')
        for i, f in enumerate(files):
            if f and f.filename:
                img_path = save_image(f, folder='products')
                if img_path:
                    pi = ProductImage(product_id=product.id, image_url=img_path, is_primary=(i == 0))
                    db.session.add(pi)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', form=form, title='Add Product')

@admin_bp.route('/products/edit/<int:pid>', methods=['GET', 'POST'])
@admin_required
def edit_product(pid):
    product = Product.query.get_or_404(pid)
    form    = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]
    if form.validate_on_submit():
        product.name          = form.name.data
        product.description   = form.description.data
        product.short_desc    = form.short_desc.data
        product.price         = form.price.data
        product.sale_price    = form.sale_price.data or None
        product.stock         = form.stock.data
        product.sku           = form.sku.data
        product.brand         = form.brand.data
        product.category_id   = form.category_id.data
        product.is_featured   = form.is_featured.data
        product.is_bestseller = form.is_bestseller.data
        product.is_new_arrival= form.is_new_arrival.data
        product.is_flash_sale = form.is_flash_sale.data
        product.is_premium    = form.is_premium.data
        product.is_limited    = form.is_limited.data
        product.cod_available = form.cod_available.data
        product.free_shipping = form.free_shipping.data
        files = request.files.getlist('images')
        for i, f in enumerate(files):
            if f and f.filename:
                img_path = save_image(f, folder='products')
                if img_path:
                    pi = ProductImage(product_id=product.id, image_url=img_path, is_primary=False)
                    db.session.add(pi)
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', form=form, product=product, title='Edit Product')

@admin_bp.route('/products/delete/<int:pid>', methods=['POST'])
@admin_required
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/image/delete/<int:img_id>', methods=['POST'])
@admin_required
def delete_product_image(img_id):
    img = ProductImage.query.get_or_404(img_id)
    db.session.delete(img)
    db.session.commit()
    return jsonify({'success': True})

# ─── Categories ───────────────────────────────────────────────────────────────
@admin_bp.route('/categories')
@admin_required
def categories():
    cats = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=cats)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        base, counter = slug, 1
        while Category.query.filter_by(slug=slug).first():
            slug = f'{base}-{counter}'; counter += 1
        img_path = None
        if form.image.data:
            img_path = save_image(form.image.data, folder='categories')
        cat = Category(name=form.name.data, slug=slug,
                       description=form.description.data,
                       icon=form.icon.data, image=img_path,
                       is_active=form.is_active.data)
        db.session.add(cat)
        db.session.commit()
        flash('Category added!', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', form=form, title='Add Category')

@admin_bp.route('/categories/edit/<int:cid>', methods=['GET', 'POST'])
@admin_required
def edit_category(cid):
    cat  = Category.query.get_or_404(cid)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name        = form.name.data
        cat.description = form.description.data
        cat.icon        = form.icon.data
        cat.is_active   = form.is_active.data
        if form.image.data:
            img_path = save_image(form.image.data, folder='categories')
            if img_path:
                cat.image = img_path
        db.session.commit()
        flash('Category updated!', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/category_form.html', form=form, category=cat, title='Edit Category')

@admin_bp.route('/categories/delete/<int:cid>', methods=['POST'])
@admin_required
def delete_category(cid):
    cat = Category.query.get_or_404(cid)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'info')
    return redirect(url_for('admin.categories'))

# ─── Orders ───────────────────────────────────────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def orders():
    page   = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query  = Order.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/orders.html', orders=orders.items, pagination=orders, current_status=status)

@admin_bp.route('/orders/<int:oid>')
@admin_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:oid>/status', methods=['POST'])
@admin_required
def update_order_status(oid):
    order  = Order.query.get_or_404(oid)
    status = request.form.get('status')
    if status in Order.STATUS_LABELS:
        order.status = status
        # Notify user
        notif = Notification(
            user_id = order.user_id,
            title   = f'Order {order.order_number} Update',
            message = f'Your order status changed to: {Order.STATUS_LABELS[status][0]}',
            type    = Order.STATUS_LABELS[status][1],
            link    = url_for('user.order_detail', order_number=order.order_number)
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'Order status updated to {status}.', 'success')
    return redirect(url_for('admin.order_detail', oid=oid))

# ─── Users ────────────────────────────────────────────────────────────────────
@admin_bp.route('/users')
@admin_required
def users():
    page  = request.args.get('page', 1, type=int)
    q     = request.args.get('q', '')
    query = User.query.filter_by(is_admin=False)
    if q:
        query = query.filter(
            (User.email.ilike(f'%{q}%')) | (User.username.ilike(f'%{q}%')))
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users.items, pagination=users, q=q)

@admin_bp.route('/users/<int:uid>/ban', methods=['POST'])
@admin_required
def ban_user(uid):
    user = User.query.get_or_404(uid)
    user.is_banned = not user.is_banned
    db.session.commit()
    action = 'banned' if user.is_banned else 'unbanned'
    flash(f'User {action}.', 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:uid>/delete', methods=['POST'])
@admin_required
def delete_user(uid):
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.users'))

# ─── Reviews ──────────────────────────────────────────────────────────────────
@admin_bp.route('/reviews')
@admin_required
def reviews():
    page    = request.args.get('page', 1, type=int)
    pending = request.args.get('pending', '0') == '1'
    query   = Review.query
    if pending:
        query = query.filter_by(is_approved=False)
    reviews = query.order_by(Review.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/reviews.html', reviews=reviews.items, pagination=reviews, pending=pending)

@admin_bp.route('/reviews/<int:rid>/approve', methods=['POST'])
@admin_required
def approve_review(rid):
    review = Review.query.get_or_404(rid)
    review.is_approved = True
    db.session.commit()
    flash('Review approved.', 'success')
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/reviews/<int:rid>/delete', methods=['POST'])
@admin_required
def delete_review(rid):
    review = Review.query.get_or_404(rid)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'info')
    return redirect(url_for('admin.reviews'))

# ─── Coupons ──────────────────────────────────────────────────────────────────
@admin_bp.route('/coupons')
@admin_required
def coupons():
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin/coupons.html', coupons=coupons)

@admin_bp.route('/coupons/add', methods=['GET', 'POST'])
@admin_required
def add_coupon():
    form = CouponForm()
    if form.validate_on_submit():
        coupon = Coupon(
            code=form.code.data.upper(),
            discount_type=form.discount_type.data,
            discount_value=form.discount_value.data,
            min_order=form.min_order.data or 0,
            max_uses=form.max_uses.data or 100,
            is_active=form.is_active.data,
        )
        db.session.add(coupon)
        db.session.commit()
        flash('Coupon created!', 'success')
        return redirect(url_for('admin.coupons'))
    return render_template('admin/coupon_form.html', form=form, title='Add Coupon')

@admin_bp.route('/coupons/delete/<int:cid>', methods=['POST'])
@admin_required
def delete_coupon(cid):
    coupon = Coupon.query.get_or_404(cid)
    db.session.delete(coupon)
    db.session.commit()
    flash('Coupon deleted.', 'info')
    return redirect(url_for('admin.coupons'))

# ─── Banners ──────────────────────────────────────────────────────────────────
@admin_bp.route('/banners')
@admin_required
def banners():
    banners = Banner.query.order_by(Banner.order).all()
    return render_template('admin/banners.html', banners=banners)

@admin_bp.route('/banners/add', methods=['GET', 'POST'])
@admin_required
def add_banner():
    if request.method == 'POST':
        title    = request.form.get('title')
        subtitle = request.form.get('subtitle')
        link     = request.form.get('link')
        order    = request.form.get('order', 0, type=int)
        img_path = None
        if 'image' in request.files:
            img_path = save_image(request.files['image'], folder='banners', size=(1920, 600))
        banner = Banner(title=title, subtitle=subtitle, link=link, image=img_path, order=order)
        db.session.add(banner)
        db.session.commit()
        flash('Banner added!', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banner_form.html', title='Add Banner')

@admin_bp.route('/banners/delete/<int:bid>', methods=['POST'])
@admin_required
def delete_banner(bid):
    banner = Banner.query.get_or_404(bid)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted.', 'info')
    return redirect(url_for('admin.banners'))

# ─── Newsletter ───────────────────────────────────────────────────────────────
@admin_bp.route('/newsletter')
@admin_required
def newsletter():
    subs = Newsletter.query.order_by(Newsletter.created_at.desc()).all()
    return render_template('admin/newsletter.html', subscribers=subs)

# ─── Export orders CSV ────────────────────────────────────────────────────────
@admin_bp.route('/orders/export')
@admin_required
def export_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order #', 'Customer', 'Status', 'Total', 'Payment', 'Date'])
    for o in orders:
        writer.writerow([o.order_number, o.user.full_name, o.status,
                         o.total, o.payment_method, o.created_at.strftime('%Y-%m-%d')])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='orders.csv')
