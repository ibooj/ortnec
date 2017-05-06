import random
from sqlalchemy.sql import func
from app import db, Category, Video

db.drop_all()
db.create_all()

for i in range(1, 11):
    c = Category(name='Category %s' % i)
    db.session.add(c)

for i in range(1, 101):
    v = Video(title='Title %s' % i)
    db.session.add(v)

db.session.commit()

for i in Video.query.all():
    for c in Category.query.order_by(func.random())[:random.randint(1, 5)]:
        i.categories.append(c)
    db.session.commit()
