import os
import uuid
import re
from PIL import Image
from flask import current_app

def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])

def save_image(file, folder='products', size=(800, 800)):
    """Save uploaded image, resize it, return relative path."""
    if not file or not file.filename or not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    try:
        img = Image.open(file)
        img.thumbnail(size, Image.LANCZOS)
        img.save(filepath, optimize=True, quality=85)
    except Exception:
        return None
    return f"{folder}/{filename}"

def slugify(text):
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text or 'product'

def generate_order_number():
    return f"TLT-{uuid.uuid4().hex[:8].upper()}"

def format_price(amount):
    try:
        return f"Rs.{float(amount):,.0f}"
    except (TypeError, ValueError):
        return "Rs.0"

def paginate_query(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)
