from ORM import orm


class Shop(orm.Model):
    __table__ = 'shop'
    id = orm.IntegerField(primary_key=True)
    shop_id = orm.StringField(ddl='varchar(100)')
    shop_url = orm.StringField(ddl='varchar(100)')
    create_time = orm.DateTimeField()
