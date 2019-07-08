from ORM import orm


class Categorys(orm.Model):
    __table__ = 'categorys'
    id = orm.IntegerField(primary_key=True)
    parent_id = orm.IntegerField(primary_key=False)
    name = orm.StringField(ddl='varchar(100)')
    priority = orm.IntegerField(primary_key=False)
    image = orm.StringField(ddl='varchar(100)')


class Category_Cid(orm.Model):
    __table__ = 'category_cid'
    id = orm.IntegerField(primary_key=True)
    category_id = orm.IntegerField(primary_key=False)
    cid = orm.IntegerField(primary_key=False)

class Luban_Categorys(orm.Model):
    __table__ = 'luban_categorys'
    id = orm.IntegerField(primary_key=True)
    parent_id = orm.IntegerField(primary_key=False)
    name = orm.StringField(ddl='varchar(100)')
    level = orm.IntegerField(primary_key=False)
