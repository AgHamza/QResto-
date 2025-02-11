from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_user, logout_user, current_user, login_required
from . import db
from .models import User, Menu, Category, Item
from .forms import RegistrationForm, LoginForm, MenuForm, CategoryForm, ItemForm
import io
import qrcode

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # Create an empty menu for the new user
        menu = Menu(restaurant_name=f"{user.username}'s Restaurant", owner=user)
        db.session.add(menu)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    menu_form = MenuForm(obj=current_user.menu)
    if menu_form.validate_on_submit():
        current_user.menu.restaurant_name = menu_form.restaurant_name.data
        db.session.commit()
        flash('Restaurant name updated.')
        return redirect(url_for('main.dashboard'))
    categories = current_user.menu.categories.all() if current_user.menu else []
    return render_template('dashboard.html', menu_form=menu_form, categories=categories)

@main.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, menu=current_user.menu)
        db.session.add(category)
        db.session.commit()
        flash('Category added.')
        return redirect(url_for('main.dashboard'))
    # Pass both the category form and dashboard data
    return render_template('dashboard.html',
                           category_form=form,
                           menu_form=MenuForm(obj=current_user.menu),
                           categories=current_user.menu.categories.all())

@main.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.')
        return redirect(url_for('main.dashboard'))
    return render_template('dashboard.html',
                           category_form=form,
                           menu_form=MenuForm(obj=current_user.menu),
                           categories=current_user.menu.categories.all())

@main.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.')
    return redirect(url_for('main.dashboard'))

@main.route('/add_item/<int:category_id>', methods=['GET', 'POST'])
@login_required
def add_item(category_id):
    category = Category.query.get_or_404(category_id)
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            description=form.description.data,
            price=float(form.price.data),
            category=category
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added.')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_item.html', form=form, category=category, action='Add')

@main.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.price = float(form.price.data)
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_item.html', form=form, item=item, action='Edit')

@main.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('main.dashboard'))

@main.route('/menu')
def menu():
    # Public menu page – expects a ?user_id= parameter in the URL
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        flash('No menu specified.')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    menu = user.menu
    categories = menu.categories.all() if menu else []
    return render_template('menu.html', menu=menu, categories=categories)

@main.route('/qr')
@login_required
def generate_qr():
    # Generate a QR code that links to the public menu page
    menu_url = url_for('main.menu', user_id=current_user.id, _external=True)
    qr_img = qrcode.make(menu_url)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='menu_qr.png')
