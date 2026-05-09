from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import (StringField, PasswordField, BooleanField, TextAreaField,
                     SelectField, FloatField, IntegerField, HiddenField, EmailField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo,
                                 NumberRange, Optional, ValidationError)
from models import User

# ─── Auth Forms ───────────────────────────────────────────────────────────────
class LoginForm(FlaskForm):
    email    = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username   = StringField('Username', validators=[DataRequired(), Length(3, 80)])
    email      = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 80)])
    last_name  = StringField('Last Name', validators=[DataRequired(), Length(2, 80)])
    phone      = StringField('Phone', validators=[Optional(), Length(max=20)])
    password   = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    confirm    = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(8, 128)])
    confirm  = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

# ─── Profile Forms ────────────────────────────────────────────────────────────
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 80)])
    last_name  = StringField('Last Name', validators=[DataRequired(), Length(2, 80)])
    phone      = StringField('Phone', validators=[Optional(), Length(max=20)])
    avatar     = FileField('Profile Picture', validators=[
        Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

class ChangePasswordForm(FlaskForm):
    current  = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(8, 128)])
    confirm  = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class AddressForm(FlaskForm):
    label       = StringField('Label', validators=[DataRequired(), Length(max=50)])
    full_name   = StringField('Full Name', validators=[DataRequired()])
    phone       = StringField('Phone', validators=[DataRequired()])
    address1    = StringField('Address Line 1', validators=[DataRequired()])
    address2    = StringField('Address Line 2', validators=[Optional()])
    city        = StringField('City', validators=[DataRequired()])
    state       = StringField('State / Province', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    country     = StringField('Country', validators=[DataRequired()])
    is_default  = BooleanField('Set as Default')

# ─── Product / Admin Forms ────────────────────────────────────────────────────
class ProductForm(FlaskForm):
    name           = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    description    = TextAreaField('Description', validators=[DataRequired()])
    short_desc     = StringField('Short Description', validators=[Optional(), Length(max=500)])
    price          = FloatField('Price (Rs.)', validators=[DataRequired(), NumberRange(min=0)])
    sale_price     = FloatField('Sale Price (Rs.)', validators=[Optional(), NumberRange(min=0)])
    stock          = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    sku            = StringField('SKU', validators=[Optional()])
    brand          = StringField('Brand', validators=[Optional()])
    category_id    = SelectField('Category', coerce=int, validators=[DataRequired()])
    is_featured    = BooleanField('Featured')
    is_bestseller  = BooleanField('Best Seller')
    is_new_arrival = BooleanField('New Arrival')
    is_flash_sale  = BooleanField('Flash Sale')
    is_premium     = BooleanField('Premium')
    is_limited     = BooleanField('Limited Edition')
    cod_available  = BooleanField('COD Available', default=True)
    free_shipping  = BooleanField('Free Shipping')
    images         = MultipleFileField('Product Images', validators=[
        Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])

class CategoryForm(FlaskForm):
    name        = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    icon        = StringField('Icon Class (FontAwesome)', validators=[Optional()])
    image       = FileField('Category Image', validators=[
        Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    is_active   = BooleanField('Active', default=True)

class CouponForm(FlaskForm):
    code           = StringField('Coupon Code', validators=[DataRequired(), Length(max=50)])
    discount_type  = SelectField('Discount Type', choices=[('percent', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = FloatField('Discount Value', validators=[DataRequired(), NumberRange(min=0)])
    min_order      = FloatField('Minimum Order', validators=[Optional(), NumberRange(min=0)])
    max_uses       = IntegerField('Max Uses', validators=[Optional(), NumberRange(min=1)])
    is_active      = BooleanField('Active', default=True)

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(5,'5 Stars'),(4,'4 Stars'),(3,'3 Stars'),(2,'2 Stars'),(1,'1 Star')], coerce=int)
    title  = StringField('Review Title', validators=[Optional(), Length(max=200)])
    body   = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10)])

class CheckoutForm(FlaskForm):
    full_name      = StringField('Full Name', validators=[DataRequired()])
    phone          = StringField('Phone', validators=[DataRequired()])
    address1       = StringField('Address Line 1', validators=[DataRequired()])
    address2       = StringField('Address Line 2', validators=[Optional()])
    city           = StringField('City', validators=[DataRequired()])
    state          = StringField('State / Province', validators=[DataRequired()])
    postal_code    = StringField('Postal Code', validators=[Optional()])
    country        = StringField('Country', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit / Debit Card'),
        ('paypal', 'PayPal'),
    ])
    coupon_code    = StringField('Coupon Code', validators=[Optional()])
    notes          = TextAreaField('Order Notes', validators=[Optional()])

class NewsletterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
