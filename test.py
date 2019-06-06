import asyncio
from ORM import orm
from config import configs
from Models.Goods import Goods,Goods_Item,Goods_Tmp
import datetime

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    tmp = Goods_Tmp()
    tmp.goods_id = 1
    tmp.add_num = 2
    tmp.edit_time = datetime.datetime.now()
    loop.run_until_complete(tmp.save())
    loop.run_until_complete(Goods_Tmp.del_by('goods_id=?',1))