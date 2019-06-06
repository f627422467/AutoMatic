from ORM import orm
import tools


class Goods(orm.Model):
    __table__ = 'goods'
    id = orm.IntegerField(primary_key=True)
    shop_id = orm.IntegerField(primary_key=False)
    goods_id = orm.StringField(ddl='varchar(100)')
    goods_name = orm.StringField(ddl='varchar(5000)')
    goods_url = orm.StringField(ddl='varchar(5000)')
    goods_picture_url = orm.StringField(ddl='varchar(5000)')
    goods_price = orm.StringField(ddl='varchar(100)')
    cid = orm.IntegerField(primary_key=False)
    sell_num = orm.IntegerField(primary_key=False)
    add_num = orm.IntegerField(primary_key=False)
    item_last_sell_num = orm.IntegerField(primary_key=False)
    is_selling = orm.BooleanField(default=True)
    create_time = orm.DateTimeField()
    edit_time = orm.DateTimeField()


class Goods_Item(orm.Model):
    __table__ = 'goods_item'
    id = orm.IntegerField(primary_key=True)
    goods_id = orm.IntegerField(primary_key=False)
    sell_num = orm.IntegerField(primary_key=False)
    add_num = orm.IntegerField(primary_key=False)
    create_time = orm.DateTimeField()


class Goods_Tmp(orm.Model):
    __table__ = tools.get_temp_table()
    id = orm.IntegerField(primary_key=True)
    goods_id = orm.IntegerField(primary_key=False)
    add_num = orm.IntegerField(primary_key=False)
    sell_num = orm.IntegerField(primary_key=False)
    edit_time = orm.DateTimeField()

