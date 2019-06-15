from Demo import test_producer, test_producer_consumer, test_consumer
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

    # query_time = '2019-06-14 20:00:00'
    query_time = '3348546531090388329'
    print(query_time)
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    # and is_selling=? ,True
    goods = loop.run_until_complete(Goods.findAll('goods_id=?', query_time))

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

    # 初始化
    q_data = queue.Queue(maxsize=30000)
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    global_goods_ids = []
    global_not_goods_ids = []

    for i in range(3):
        p = test_producer.Producer(i, q_task, q_data, event, global_goods_ids, global_not_goods_ids)
        p.start()

    q_goods = queue.Queue(maxsize=30000)
    q_goods_item = queue.Queue(maxsize=30000)
    q_goods_tmp = queue.Queue(maxsize=30000)

    for i in range(3):
        pc = test_producer_consumer.Consumer(i, q_data, q_goods, q_goods_item, q_goods_tmp, event, goods_id_object,cids)
        pc.daemon = True
        pc.start()

    q_stop = queue.Queue(maxsize=10)
    c1 = test_consumer.Consumer(1, q_goods, q_stop, event, 'goods_update',loop)
    c1.daemon = True
    c1.start()
    c2 = test_consumer.Consumer(2, q_goods_item, q_stop, event, 'goods_item',loop)
    c2.daemon = True
    c2.start()
    c3 = test_consumer.Consumer(3, q_goods_tmp, q_stop, event, 'goods_tmp',loop)
    c3.daemon = True
    c3.start()

    q_task.join()
    q_data.join()
    q_goods.join()
    q_goods_item.join()
    q_goods_tmp.join()
    q_stop.join()
    print("主程序结束")
