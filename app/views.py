from flask import request, redirect, render_template, url_for
from flask_login import login_user, current_user, \
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
        logged_id = current_user.id
    else:
        logged_name = ''
        logged_id = 0

    return render_template('index.html', current_user=logged_name, logged_id=logged_id)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    # check if user is not authenticated, if so, sign him up
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # check if either username or email already exists
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

    # log out the current user, and return back to the home page
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

        # check if user exists or not
        existing_user = user_store.get_by_name_or_mail(user_identity)
        if not existing_user:
            return "User doesn't exist!", 405

        if not existing_user.verify_password(password):
            return "Invalid password", 405

        login_user(existing_user, remember=True)
        return redirect(url_for('home'))


@app.route('/catalog/<string:category_name>/items')
def show_catalog(category_name):

    # show all categories and last added item in homepage
    item_category = category_store.get_by_name(category_name)

    items = item_store.get_all_items_by_category(item_category.id)
    if current_user.is_authenticated:
        logged_name = current_user.username
        logged_id = current_user.id
    else:
        logged_name = ''
        logged_id = 0

    return render_template('category.html', category=item_category,
                           category_id=item_category.id, items=items,
                           current_user=logged_name,
                           logged_id=logged_id)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_item(category_name, item_name):

    # view requested catalog
    category = category_store.get_by_name(category_name)
    item = item_store.get_item_by_name_and_category(category.id, item_name)

    if current_user.is_authenticated:
        logged_name = current_user.username
        logged_id = current_user.id
    else:
        logged_name = ''
        logged_id = 0
    return render_template('item.html', item=item,
                           category=category_name, current_user=logged_name,
                           logged_id=logged_id)


@app.route('/add/category', methods=['GET', 'POST'])
@login_required
def add_category():

    # add new catalog if user is authenticated
    if request.method == 'GET':
        return render_template('add_category.html')

    elif request.method == 'POST':
        category_name = request.form['category']
        new_category = Category(name=category_name, user_id=current_user.id)
        category_store.add(new_category)
        return redirect(url_for('home'))


@app.route('/add/item', methods=['GET', 'POST'])
@login_required
def add_item():

    # add new item if user is authenticated
    if request.method == 'GET':
        categories = category_store.get_all()
        return render_template('add_item.html', categories=categories)

    elif request.method == 'POST':
        category_id = request.form['category']
        item_name = request.form['item_name']
        item_description = request.form['description']
        new_item = Item(name=item_name,
                        description=item_description, category_id=category_id,
                        user_id=current_user.id)
        item_store.add(new_item)
        return redirect(url_for('home'))


@app.route('/category/edit/<int:category_id>', methods=['GET'])
@login_required
def edit_category(category_id):

    # update selected category if the user is authenticated and the owner of the catalog
    current_category = category_store.get_by_id(category_id)
    if not current_category:
        return "Category doesn't exist", 405

    # if the category doesn't belong to the user, reject the update
    if current_category.user_id != current_user.id:
        return "Sorry, you don't have the right to edit this category!", 405

    if request.method == 'GET':
        return render_template('edit_category.html', category=current_category)


@app.route('/item/edit/<int:item_id>', methods=['GET'])
@login_required
def edit_item(item_id):

    # update selected item if the user is authenticated and the owner of it.
    current_item = item_store.get_by_id(item_id)
    if not current_item:
        return "Item doesn't exist", 405

    # if the item doesn't belong to the user, reject the update
    if current_item.user_id != current_user.id:
        return "Sorry, you don't have the right to edit this item!", 405

    if request.method == 'GET':
        categories = category_store.get_all()
        return render_template('edit_item.html',
                               categories=categories, item=current_item)


@app.route('/category/delete/<int:category_id>', methods=['GET'])
@login_required
def delete_category(category_id):

    # delete selected catalog if user is logged in and the owner of it
    category_to_delete = category_store.get_by_id(category_id)

    if not category_to_delete:
        return "Category doesn't exist!", 405

    if category_to_delete.user_id != current_user.id:
        return "Sorry, you don't have the right to delete this category!", 405

    return render_template('delete.html',
                           object_type='category', object_id=category_id)


@app.route('/item/delete/<int:item_id>', methods=['GET'])
@login_required
def delete_item(item_id):

    # delete selected item if user is logged in and the owner of it
    item_to_delete = item_store.get_by_id(item_id)

    if not item_to_delete:
        return "Item doesn't exist!", 405

    if item_to_delete.user_id != current_user.id:
        return "Sorry, you don't have the right to delete this item!", 405

    return render_template('delete.html',
                           object_type='item', object_id=item_id)
