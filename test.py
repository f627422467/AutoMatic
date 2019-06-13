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
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    # goods = loop.run_until_complete(Goods.find_one('goods_id=?', 3337801828476828209))

    # batch_temps = []
    # for i in range(30000):
    #     temp = Temp()
    #     temp.TableId = i
    #     temp.TableName = "123"+str(i)
    #     temp.DateTime = datetime.datetime.now()
    #     batch_temps.append(temp)
    batch_temps = loop.run_until_complete(Temp.findAll())
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))
    for temp in batch_temps:
        temp.DateTime = datetime.datetime.now()
    # loop.run_until_complete(Temp.batch_insert(batch_temps))

    loop.run_until_complete(Temp.batch_update(batch_temps))
    # print(goods)
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))

