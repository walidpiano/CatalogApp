from app import models, db
from app import stores

db.drop_all()
db.create_all()


user = models.User(username='walid', email='walidpianooo@gmail.com')
user.hash_password('wwzzaa')

user_store = stores.UserStore()
user_store.add(user)

cat1 = models.Category(name='Sports', user_id=user.id)
cat2 = models.Category(name='Music',user_id=user.id)
cat3 = models.Category(name='Art', user_id=user.id)

cat_store = stores.CategoryStore()
cat_store.add(cat1)
cat_store.add(cat2)
cat_store.add(cat3)

dummy_items = {
    models.Item(name='Football', description="It's the most popular sport in the world!", category_id=cat1.id, user_id=user.id),
    models.Item(name='Basketball', description="It's the most amusing for many Americans!", category_id=cat1.id, user_id=user.id),
    models.Item(name='Karate', description="It's a good sport to defend yourself!", category_id=cat1.id, user_id=user.id),
    models.Item(name='Piano', description="I really love playing piano!", category_id=cat2.id, user_id=user.id),
    models.Item(name='Violin', description="It's one of the most important instruments in Orchestra!", category_id=cat2.id, user_id=user.id),
    models.Item(name='Drawing', description="Everyone can try it!", category_id=cat3.id, user_id=user.id),
}

item_store = stores.ItemStore()
for i in dummy_items:
    item_store.add(i)

print('done!')


