from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session, jsonify, abort)
from flask_login import login_user, logout_user, login_required, current_user
from models import (db, User, Product, Category, Cart, CartItem, Order, OrderItem,
                    Wishlist, Review, Address, Notification, Newsletter, Coupon, Banner)
from forms import (LoginForm, RegisterForm, ProfileForm, ChangePasswordForm,
                   AddressForm, ReviewForm, CheckoutForm, NewsletterForm, SearchForm)
from utils import save_image, generate_order_number, slugify
from datetime import datetime
import json

user_bp = Blueprint('user', __name__)

# ─── Home ─────────────────────────────────────────────────────────────────────
@user_bp.route('/')
def home():
    banners       = Banner.query.filter_by(is_active=True).order_by(Banner.order).all()
    featured      = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    bestsellers   = Product.query.filter_by(is_bestseller=True, is_active=True).limit(8).all()
    new_arrivals  = Product.query.filter_by(is_new_arrival=True, is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    flash_sale    = Product.query.filter_by(is_flash_sale=True, is_active=True).limit(8).all()
    premium       = Product.query.filter_by(is_premium=True, is_active=True).limit(4).all()
    limited       = Product.query.filter_by(is_limited=True, is_active=True).limit(4).all()
    top_rated     = Product.query.filter_by(is_active=True).order_by(Product.views.desc()).limit(8).all()
    categories    = Category.query.filter_by(is_active=True).all()
    cod_products  = Product.query.filter_by(cod_available=True, is_active=True).limit(4).all()
    free_ship     = Product.query.filter_by(free_shipping=True, is_active=True).limit(4).all()
    return render_template('user/home.html',
        banners=banners, featured=featured, bestsellers=bestsellers,
        new_arrivals=new_arrivals, flash_sale=flash_sale, premium=premium,
        limited=limited, top_rated=top_rated, categories=categories,
        cod_products=cod_products, free_ship=free_ship)

# ─── Auth ─────────────────────────────────────────────────────────────────────
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_banned:
                flash('Your account has been banned. Contact support.', 'danger')
                return redirect(url_for('user.login'))
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page or url_for('user.home'))
        flash('Invalid email or password.', 'danger')
    return render_template('user/login.html', form=form)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # Create empty cart
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
        login_user(user)
        flash('Account created successfully! Welcome to Talatum.', 'success')
        return redirect(url_for('user.home'))
    return render_template('user/register.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.home'))

# ─── Products ─────────────────────────────────────────────────────────────────
@user_bp.route('/products')
def products():
    page     = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    sort     = request.args.get('sort', 'newest')
    min_p    = request.args.get('min_price', 0, type=float)
    max_p    = request.args.get('max_price', 9999999, type=float)
    brand    = request.args.get('brand', '')
    q        = request.args.get('q', '')

    flash_sale = request.args.get('is_flash_sale', '')
    query = Product.query.filter_by(is_active=True)
    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if flash_sale:
        query = query.filter_by(is_flash_sale=True)
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
    if brand:
        query = query.filter(Product.brand.ilike(f'%{brand}%'))
    query = query.filter(Product.price >= min_p, Product.price <= max_p)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    pagination  = query.paginate(page=page, per_page=12, error_out=False)
    categories  = Category.query.filter_by(is_active=True).all()
    brands      = db.session.query(Product.brand).filter(Product.brand != None).distinct().all()
    return render_template('user/products.html',
        products=pagination.items, pagination=pagination,
        categories=categories, brands=[b[0] for b in brands],
        current_category=category, current_sort=sort, q=q)

@user_bp.route('/product/<slug>')
def product_detail(slug):
    product  = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    product.views += 1
    db.session.commit()
    related  = Product.query.filter_by(category_id=product.category_id, is_active=True)\
                            .filter(Product.id != product.id).limit(4).all()
    reviews  = product.reviews.filter_by(is_approved=True).order_by(Review.created_at.desc()).all()
    in_wish  = False
    if current_user.is_authenticated:
        in_wish = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None
    form = ReviewForm()
    return render_template('user/product_detail.html',
        product=product, related=related, reviews=reviews,
        in_wishlist=in_wish, form=form)

# ─── Cart ─────────────────────────────────────────────────────────────────────
@user_bp.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return render_template('user/cart.html', cart=cart)

@user_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity   = request.form.get('quantity', 1, type=int)
    variant    = request.form.get('variant', '')
    product    = Product.query.get_or_404(product_id)
    cart       = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.flush()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity, variant=variant)
        db.session.add(item)
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'cart_count': cart.item_count, 'message': 'Added to cart!'})
    flash('Product added to cart!', 'success')
    return redirect(url_for('user.cart'))

@user_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    item_id  = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    item     = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        abort(403)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return redirect(url_for('user.cart'))

@user_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('user.cart'))

# ─── Checkout ─────────────────────────────────────────────────────────────────
@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or cart.item_count == 0:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('user.cart'))
    form = CheckoutForm()
    default_addr = Address.query.filter_by(user_id=current_user.id, is_default=True).first()
    if form.validate_on_submit():
        subtotal = cart.total
        shipping = 0 if subtotal >= 5000 else 200
        tax      = round(subtotal * 0.05, 2)
        discount = 0
        coupon   = None
        if form.coupon_code.data:
            coupon = Coupon.query.filter_by(code=form.coupon_code.data.upper(), is_active=True).first()
            if coupon and coupon.used_count < coupon.max_uses:
                if coupon.discount_type == 'percent':
                    discount = round(subtotal * coupon.discount_value / 100, 2)
                else:
                    discount = coupon.discount_value
                coupon.used_count += 1
        total = subtotal + shipping + tax - discount
        order = Order(
            order_number   = generate_order_number(),
            user_id        = current_user.id,
            payment_method = form.payment_method.data,
            subtotal       = subtotal,
            shipping_cost  = shipping,
            tax            = tax,
            discount       = discount,
            total          = total,
            coupon_code    = form.coupon_code.data or None,
            notes          = form.notes.data,
            ship_name      = form.full_name.data,
            ship_phone     = form.phone.data,
            ship_address1  = form.address1.data,
            ship_address2  = form.address2.data,
            ship_city      = form.city.data,
            ship_state     = form.state.data,
            ship_postal    = form.postal_code.data,
            ship_country   = form.country.data,
        )
        db.session.add(order)
        db.session.flush()
        for ci in cart.items:
            oi = OrderItem(
                order_id     = order.id,
                product_id   = ci.product_id,
                product_name = ci.product.name,
                product_img  = ci.product.main_image,
                quantity     = ci.quantity,
                price        = ci.product.effective_price,
                variant      = ci.variant,
            )
            db.session.add(oi)
            # Reduce stock
            ci.product.stock = max(0, ci.product.stock - ci.quantity)
        # Clear cart
        for ci in cart.items.all():
            db.session.delete(ci)
        # Notification
        notif = Notification(
            user_id = current_user.id,
            title   = 'Order Placed!',
            message = f'Your order {order.order_number} has been placed successfully.',
            type    = 'success',
            link    = url_for('user.order_detail', order_number=order.order_number)
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'Order placed successfully! Order #{order.order_number}', 'success')
        return redirect(url_for('user.order_detail', order_number=order.order_number))
    return render_template('user/checkout.html', form=form, cart=cart, default_addr=default_addr)

# ─── Orders ───────────────────────────────────────────────────────────────────
@user_bp.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', orders=orders)

@user_bp.route('/order/<order_number>')
@login_required
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template('user/order_detail.html', order=order)

# ─── Wishlist ─────────────────────────────────────────────────────────────────
@user_bp.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).order_by(Wishlist.created_at.desc()).all()
    return render_template('user/wishlist.html', items=items)

@user_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    item    = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        msg, added = 'Removed from wishlist.', False
    else:
        db.session.add(Wishlist(user_id=current_user.id, product_id=product_id))
        db.session.commit()
        msg, added = 'Added to wishlist!', True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = Wishlist.query.filter_by(user_id=current_user.id).count()
        return jsonify({'success': True, 'added': added, 'message': msg, 'count': count})
    flash(msg, 'success' if added else 'info')
    return redirect(request.referrer or url_for('user.wishlist'))

# ─── Reviews ──────────────────────────────────────────────────────────────────
@user_bp.route('/review/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    form    = ReviewForm()
    if form.validate_on_submit():
        existing = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if existing:
            flash('You have already reviewed this product.', 'warning')
        else:
            review = Review(
                user_id    = current_user.id,
                product_id = product_id,
                rating     = form.rating.data,
                title      = form.title.data,
                body       = form.body.data,
            )
            db.session.add(review)
            db.session.commit()
            flash('Review submitted! It will appear after approval.', 'success')
    return redirect(url_for('user.product_detail', slug=product.slug))

# ─── Dashboard ────────────────────────────────────────────────────────────────
@user_bp.route('/dashboard')
@login_required
def dashboard():
    orders        = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()
    notifs        = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('user/dashboard.html',
        orders=orders, wishlist_count=wishlist_count, notif_count=notifs)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name  = form.last_name.data
        current_user.phone      = form.phone.data
        if form.avatar.data:
            img = save_image(form.avatar.data, folder='avatars', size=(300, 300))
            if img:
                current_user.avatar = img
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)

@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('user.dashboard'))
    return render_template('user/change_password.html', form=form)

@user_bp.route('/addresses')
@login_required
def addresses():
    addrs = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('user/addresses.html', addresses=addrs)

@user_bp.route('/address/add', methods=['GET', 'POST'])
@login_required
def add_address():
    form = AddressForm()
    if form.validate_on_submit():
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id).update({'is_default': False})
        addr = Address(user_id=current_user.id, **{
            k: v for k, v in form.data.items() if k not in ('csrf_token', 'submit')
        })
        db.session.add(addr)
        db.session.commit()
        flash('Address added!', 'success')
        return redirect(url_for('user.addresses'))
    return render_template('user/address_form.html', form=form, title='Add Address')

@user_bp.route('/address/delete/<int:addr_id>', methods=['POST'])
@login_required
def delete_address(addr_id):
    addr = Address.query.filter_by(id=addr_id, user_id=current_user.id).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash('Address deleted.', 'info')
    return redirect(url_for('user.addresses'))

# ─── Notifications ────────────────────────────────────────────────────────────
@user_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('user/notifications.html', notifications=notifs)

# ─── Search ───────────────────────────────────────────────────────────────────
@user_bp.route('/search')
def search():
    q    = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if not q:
        return redirect(url_for('user.products'))
    results    = Product.query.filter(Product.name.ilike(f'%{q}%'), Product.is_active == True)\
                              .paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('user/search.html', products=results.items,
                           pagination=results, q=q, categories=categories)

# ─── Newsletter ───────────────────────────────────────────────────────────────
@user_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email = request.form.get('email', '').strip()
    if email:
        from models import Newsletter
        existing = Newsletter.query.filter_by(email=email).first()
        if not existing:
            db.session.add(Newsletter(email=email))
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Subscribed successfully!'})
            flash('Subscribed to newsletter!', 'success')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Already subscribed.'})
            flash('Already subscribed.', 'info')
    return redirect(request.referrer or url_for('user.home'))

# ─── Category page ────────────────────────────────────────────────────────────
@user_bp.route('/category/<slug>')
def category(slug):
    cat      = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    page     = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category_id=cat.id, is_active=True)\
                            .paginate(page=page, per_page=12, error_out=False)
    return render_template('user/category.html', category=cat,
                           products=products.items, pagination=products)

# ─── Apply coupon (AJAX) ──────────────────────────────────────────────────────
@user_bp.route('/coupon/apply', methods=['POST'])
@login_required
def apply_coupon():
    code   = request.json.get('code', '').upper()
    cart   = Cart.query.filter_by(user_id=current_user.id).first()
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if not coupon:
        return jsonify({'success': False, 'message': 'Invalid coupon code.'})
    if coupon.used_count >= coupon.max_uses:
        return jsonify({'success': False, 'message': 'Coupon usage limit reached.'})
    if cart.total < coupon.min_order:
        return jsonify({'success': False, 'message': f'Minimum order Rs.{coupon.min_order:,.0f} required.'})
    if coupon.discount_type == 'percent':
        discount = round(cart.total * coupon.discount_value / 100, 2)
    else:
        discount = coupon.discount_value
    return jsonify({'success': True, 'discount': discount,
                    'message': f'Coupon applied! You save Rs.{discount:,.0f}'})
