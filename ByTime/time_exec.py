import sys
sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from ByTime import time_producer
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

if __name__ == '__main__':

    query_time = '2019-06-16 21:42:00'
    # query_time = '3348546531090388329'
    print(query_time)
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    # and is_selling=? ,True
    goods = loop.run_until_complete(Goods.findAll('edit_time<?and is_selling=?', [query_time, True]))
    # goods = loop.run_until_complete(Goods.findAll('goods_id=?', "3349284677054817291"))

    q_task = queue.Queue(maxsize=0)
    for good in goods:
        q_task.put(good.goods_id)
    print("商品总数%s" % q_task.qsize())

    goods_id_object = tools.list_to_dict(goods, "goods_id")

    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)

    goods_tmp = loop.run_until_complete(Goods_Tmp.findAll())
    goods_id_tmp = tools.list_to_dict(goods_tmp, "goods_id")

    # 初始化
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    global_goods_ids = []
    global_not_goods_ids = []

    q_goods = queue.Queue(maxsize=30000)
    q_goods_item = queue.Queue(maxsize=30000)
    q_goods_tmp = queue.Queue(maxsize=30000)

    q_stop = queue.Queue(maxsize=10)
    c1 = consumer.Consumer(1, q_goods, q_stop, event, lock, 'goods_update', loop)
    c1.daemon = True
    c1.start()
    c2 = consumer.Consumer(2, q_goods_item, q_stop, event, lock, 'goods_item', loop)
    c2.daemon = True
    c2.start()
    c3 = consumer.Consumer(3, q_goods_tmp, q_stop, event, lock, 'goods_tmp', loop)
    c3.daemon = True
    c3.start()

    for i in range(900):
        p = time_producer.Producer(i, q_task, q_goods, q_goods_item, q_goods_tmp, event, global_goods_ids,
                                   goods_id_object, goods_id_tmp, cids)
        p.start()

    q_task.join()
    q_goods.join()
    q_goods_item.join()
    q_goods_tmp.join()
    q_stop.join()
    print("主程序结束")
