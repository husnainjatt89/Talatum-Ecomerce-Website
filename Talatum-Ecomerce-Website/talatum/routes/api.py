from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import db, Product, Category, Cart, CartItem, Wishlist, Order
from sqlalchemy import or_

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ─── Products ─────────────────────────────────────────────────────────────────
@api_bp.route('/products')
def get_products():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    q        = request.args.get('q', '')
    query    = Product.query.filter_by(is_active=True)
    if category:
        from models import Category as Cat
        cat = Cat.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'products': [_product_dict(p) for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
    })

@api_bp.route('/products/<int:pid>')
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(_product_dict(p, detail=True))

@api_bp.route('/search/suggestions')
def search_suggestions():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    products = Product.query.filter(
        Product.name.ilike(f'%{q}%'), Product.is_active == True
    ).limit(8).all()
    return jsonify([{'id': p.id, 'name': p.name, 'slug': p.slug,
                     'price': p.effective_price, 'image': p.main_image} for p in products])

# ─── Cart ─────────────────────────────────────────────────────────────────────
@api_bp.route('/cart')
@login_required
def get_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        return jsonify({'items': [], 'total': 0, 'count': 0})
    return jsonify({
        'items': [_cart_item_dict(i) for i in cart.items],
        'total': cart.total,
        'count': cart.item_count,
    })

@api_bp.route('/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    data       = request.get_json()
    product_id = data.get('product_id')
    quantity   = data.get('quantity', 1)
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
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'cart_count': cart.item_count})

# ─── Wishlist ─────────────────────────────────────────────────────────────────
@api_bp.route('/wishlist')
@login_required
def get_wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'product_id': i.product_id, 'product_name': i.product.name} for i in items])

# ─── Categories ───────────────────────────────────────────────────────────────
@api_bp.route('/categories')
def get_categories():
    cats = Category.query.filter_by(is_active=True).all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug, 'icon': c.icon} for c in cats])

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _product_dict(p, detail=False):
    d = {
        'id': p.id, 'name': p.name, 'slug': p.slug,
        'price': p.price, 'sale_price': p.sale_price,
        'effective_price': p.effective_price,
        'discount_percent': p.discount_percent,
        'main_image': p.main_image,
        'avg_rating': p.avg_rating,
        'review_count': p.review_count,
        'stock': p.stock,
        'brand': p.brand,
        'cod_available': p.cod_available,
        'free_shipping': p.free_shipping,
    }
    if detail:
        d['description'] = p.description
        d['images'] = [i.image_url for i in p.images]
    return d

def _cart_item_dict(i):
    return {
        'id': i.id,
        'product_id': i.product_id,
        'product_name': i.product.name,
        'product_image': i.product.main_image,
        'quantity': i.quantity,
        'price': i.product.effective_price,
        'subtotal': i.subtotal,
    }
