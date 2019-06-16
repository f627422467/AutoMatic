import tools
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods,Goods_Item,Temp
import asyncio
from config import configs
import functools
import sys
import datetime


#页面手动更新单个产品
if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    # goods = loop.run_until_complete(Goods.find_one('goods_id=?', 3337801828476828209))
    query_time = '2019-06-14 20:00:00'
    goods = loop.run_until_complete(Goods.findAll('edit_time<?', query_time))
    print("商品总数%s" % len(goods))

    start = datetime.datetime.now()
    for temp in goods:
        temp.edit_time = datetime.datetime.now()
    # loop.run_until_complete(Temp.batch_insert(batch_temps))
    # print(datetime.datetime.now())
    loop.run_until_complete(Goods.batch_update(goods))
    # print(goods)
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))

