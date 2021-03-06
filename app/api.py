from flask import jsonify, request
from flask_login import login_required, current_user

from app import app
from app import category_store, item_store


@app.route('/api/last/items')
def get_all_last_items():

    # get every category and its latest item
    categories = category_store.get_all_categories()
    list_items = []
    for category in categories:
        item = item_store.get_last_item(category.id)
        if item:
            list_items.append({
                "category_id": category.id,
                "category_name": category.name,
                "item_id": item.id,
                "item_name": item.name,
            })
        else:
            list_items.append({
                "category_id": category.id,
                "category_name": category.name,
                "item_id": "#",
                "item_name": "No Items",
            })

    return jsonify(list_items)


@app.route('/category/edit/api/category/update', methods=['PUT'])
@login_required
def update_category():

    # check if the category is found, and update it when the user is logged in and owns it.
    request_data = request.get_json()
    category_id = request_data['category_id']
    category_name = request_data['category_name']
    existing_category = category_store.get_by_id(category_id)
    if not existing_category:
        result = jsonify({"result": False})
    elif existing_category.user_id != current_user.id:
        result = jsonify({"result": False})
    else:
        existing_category.name = category_name
        category_store.update(existing_category)
        result = jsonify({"result": True})

    return result


@app.route('/item/edit/api/item/update', methods=['PUT'])
@login_required
def update_item():

    # check if the item is found, and update it when the user is logged in and owns it.
    request_data = request.get_json()
    print(request_data)
    item_id = request_data['item_id']
    category_id = request_data['category_id']
    item_name = request_data['item_name']
    item_description = request_data['item_description']
    existing_item = item_store.get_by_id(item_id)
    if not existing_item:
        result = jsonify({"result": False})
    elif existing_item.user_id != current_user.id:
        result = jsonify({"result": False})
    else:
        existing_item.category_id = category_id
        existing_item.name = item_name
        existing_item.description = item_description
        item_store.update(existing_item)
        result = jsonify({"result": True})

    return result


@app.route('/category/delete/api/category/delete/<int:category_id>',
           methods=['DELETE'])
@login_required
def remove_category(category_id):

    # if logged in, delete category with its items (user must be the owner of it)
    category_to_remove = category_store.get_by_id(category_id)
    if not category_to_remove:
        result = jsonify({"result": False})
    elif category_to_remove.user_id != current_user.id:
        result = jsonify({"result": False})
    else:
        item_store.delete_under_category(category_id)
        category_store.delete(category_id)
        result = jsonify({"result": True})

    return result


@app.route('/item/delete/api/item/delete/<int:item_id>',
           methods=['DELETE'])
@login_required
def remove_item(item_id):

    # if logged in, delete item (user must be the owner of it)
    item_to_remove = item_store.get_by_id(item_id)
    if not item_to_remove:
        result = jsonify({"result": False})
    elif item_to_remove.user_id != current_user.id:
        result = jsonify({"result": False})
    else:
        item_store.delete(item_id)
        result = jsonify({"result": True})

    return result


@app.route('/catalog.json')
def show_all():

    # return all the categories and items in json format
    result = []
    sub_result = []
    categories = category_store.get_all()
    for c in categories:
        result.append([
            c.serialize, item_store.show_categorized(c.id)
        ])

    return jsonify(result)


@app.route('/api/catalog/<string:category_name>')
def show_category_json(category_name):

    # show requested category in json format
    category = category_store.get_by_name(category_name)
    if not category:
        return jsonify({"result": "doesn't exist!"})

    return jsonify(category.serialize)


@app.route('/api/item/<string:category_name>/<string:item_name>')
def show_item_json(category_name, item_name):

    # show requested category in json format
    category = category_store.get_by_name(category_name)

    if not category:
        return jsonify({"result": "doesn't exist!"})

    item = item_store.get_item_by_name_and_category(category.id, item_name)

    if not item:
        return jsonify({"result": "doesn't exist!"})


    result = jsonify(category.serialize, item.serialize)
    return result
