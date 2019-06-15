import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from ByTime import time_producer,time_batch_producer
import consumer
import threading
import queue
import asyncio
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods, Goods_Item, Goods_Tmp
from Models.Categorys import Category_Cid
from config import configs
import time
import datetime
import tools


async def find_all_cids(loop):
    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)
    return cids


# 按照给定时间更新
if __name__ == '__main__':
    query_time = str(sys.argv[1])
    # query_time = '2019-06-14 09:00:00'
    print(query_time)
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    goods = loop.run_until_complete(Goods.findAll('edit_time<?', query_time))
    q_goods = queue.Queue(maxsize=0)
    for good in goods:
        q_goods.put_nowait(good.goods_id)
    print("商品总数%s" % q_goods.qsize())
    goods_id_object = tools.list_to_dict(goods, "goods_id")

    cids = find_all_cids(loop)

    # 初始化
    q_data = queue.Queue(maxsize=30000)
    global_goods_ids = []
    global_not_goods_ids = []
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    for i in range(400):
        p = time_batch_producer.Producer(i, q_goods, q_data, event, global_goods_ids,global_not_goods_ids)
        p.start()
