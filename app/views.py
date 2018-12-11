from flask import request, redirect, render_template, url_for
from flask_login import login_user, current_user,\
    LoginManager, login_required, logout_user

from app import app
from app import category_store, item_store, user_store
from app.models import User, Category, Item

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/home')
@app.route('/index')
def home():

    # view home page with login buttons if not logged in
    if current_user.is_authenticated:
        logged_name = current_user.username
    else:
        logged_name = ''

    return render_template('index.html', current_user=logged_name)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            if user_store.get_by_username(username):
                return "Username already exists", 405
            elif user_store.get_by_email(email):
                return "Email already exists", 405

            new_user = User(username=username, email=email)
            new_user.hash_password(password)
            user_store.add(new_user)

            # automatically login the new user
            login_user(new_user, remember=True)
            return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    # to login using credentials
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        user_identity = request.form['user_identity']
        password = request.form['password']

        existing_user = user_store.get_by_name_or_mail(user_identity)
        if not existing_user:
            return "User doesn't exist!", 405

        if not existing_user.verify_password(password):
            return "Invalid password", 405

        login_user(existing_user, remember=True)
        return redirect(url_for('home'))


@app.route('/catalog/<string:category>/items')
def show_catalog(category):
    category_id = category_store.get_id_by_name(category)
    items = item_store.get_all_items_by_category(category_id.id)
    if current_user.is_authenticated:
        logged_name = current_user.username
    else:
        logged_name = ''

    return render_template('category.html', category=category,
                           category_id=category_id.id, items=items,
                           current_user=logged_name)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_item(category_name, item_name):
    category_id = category_store.get_id_by_name(category_name)
    item = item_store.get_item_by_name_and_category(category_id.id, item_name)

    if current_user.is_authenticated:
        logged_name = current_user.username
    else:
        logged_name = ''
    return render_template('item.html', item=item,
                           category=category_name, current_user=logged_name)


@app.route('/add/category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'GET':
        return render_template('add_category.html')
    elif request.method == 'POST':
        category_name = request.form['category']
        new_category = Category(name=category_name)
        category_store.add(new_category)
        return redirect(url_for('home'))


@app.route('/add/item', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'GET':
        categories = category_store.get_all()
        return render_template('add_item.html', categories=categories)
    elif request.method == 'POST':
        category_id = request.form['category']
        item_name = request.form['item_name']
        item_description = request.form['description']
        new_item = Item(name=item_name,
                        description=item_description, category_id=category_id)
        item_store.add(new_item)
        return redirect(url_for('home'))


@app.route('/category/edit/<int:category_id>', methods=['GET'])
@login_required
def edit_category(category_id):
    current_category = category_store.get_by_id(category_id)
    if not current_category:
        return "Category doesn't exist", 405

    if request.method == 'GET':
        return render_template('edit_category.html', category=current_category)


@app.route('/item/edit/<int:item_id>', methods=['GET'])
@login_required
def edit_item(item_id):
    current_item = item_store.get_by_id(item_id)
    if not current_item:
        return "Item doesn't exist", 405

    if request.method == 'GET':
        categories = category_store.get_all()
        return render_template('edit_item.html',
                               categories=categories, item=current_item)


@app.route('/category/delete/<int:category_id>', methods=['GET'])
@login_required
def delete_category(category_id):
    return render_template('delete.html',
                           object_type='category', object_id=category_id)


@app.route('/item/delete/<int:item_id>', methods=['GET'])
@login_required
def delete_item(item_id):
    return render_template('delete.html',
                           object_type='item', object_id=item_id)
