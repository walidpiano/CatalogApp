from flask import jsonify

from app import models, db
from sqlalchemy import desc, func


class BaseStore():

    def __init__(self, data_provider):
        self.data_provider = data_provider

    def get_all(self):
        return self.data_provider.query.all()

    def add(self, entity):
        db.session.add(entity)
        db.session.commit()
        return entity

    def get_by_id(self, id):
        return self.data_provider.query.get(id)

    def update(self, entity, fields):
        result = self.data_provider.query.filter_by(id=entity.id).update(fields)
        db.session.commit()
        return result

    def delete(self, id):
        result = self.data_provider.query.filter_by(id=id).delete()
        db.session.commit()
        return result

    def entity_exists(self, entity):
        result = True

        if self.get_by_id(entity.id) is None:
            result = False

        return result


class CategoryStore(BaseStore):

    def __init__(self):
        super().__init__(models.Category)

    def get_all_categories(self):
        result = self.data_provider.query.order_by(self.data_provider.name.desc()).all()
        return result

    def get_id_by_name(self, category_name):
        result = self.data_provider.query.filter_by(name=category_name).first()
        return result

    def update(self, entity):
        fields = {"name": entity.name}
        return super().update(entity, fields)


class ItemStore(BaseStore):
    def __init__(self):
        super().__init__(models.Item)

    def get_last_item(self, category_id):
        result = self.data_provider.query.filter_by(category_id=category_id).order_by(self.data_provider.id.desc()).first()
        return result

    def get_all_items_by_category(self, category_id):
        result = self.data_provider.query.filter_by(category_id=category_id).order_by(self.data_provider.id.desc()).all()
        return result

    def get_item_by_name_and_category(self, category_id, item_name):
        result = self.data_provider.query.filter_by(category_id=category_id, name=item_name).first()
        return result

    def update(self, entity):
        fields = {"name": entity.name, "description": entity.description, "category_id": entity.category_id}
        return super().update(entity, fields)

    def delete_under_category(self, category_id):
        items = self.data_provider.query.filter_by(category_id=category_id).delete()
        return True

    def show_categorized(self, category_id):
        items = self.get_all_items_by_category(category_id)
        return [i.serialize for i in items]


class UserStore(BaseStore):
    def __init__(self):
        super().__init__(models.User)

    def get_by_username(self, username):
        result = self.data_provider.query.filter_by(username=username).first()
        return result

    def get_by_email(self, email):
        return self.data_provider.query.filter_by(email=email).first()

    def get_by_name_or_mail(self, user_info):
        result = self.get_by_username(user_info)
        if not result:
            result = self.get_by_email(user_info)
        return result
