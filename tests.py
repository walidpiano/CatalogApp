from app import models, db
from app import stores
from app import item_store, category_store

test = item_store.get_all()

for i in test:
    #print(i)
    pass

new_cat = category_store.get_id_by_name('Sports')
print(new_cat)

some_items = item_store.get_all_items_by_category(new_cat.id)
for i in some_items:
    print(i)
