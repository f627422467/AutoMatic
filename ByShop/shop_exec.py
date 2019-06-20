import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from ByShop import shop_producer, shop_producer_consumer
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

# 按照既有店铺更新商品
if __name__ == '__main__':
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    shops = loop.run_until_complete(Shop.findAll())
    # shop_id = 'pahyIe'
    # shops = loop.run_until_complete(Shop.findAll('shop_id=?', shop_id))
    q_task = queue.Queue(maxsize=0)
    for shop in shops:
        q_task.put(shop)
    print("店铺总数%s" % q_task.qsize())

    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)

    # shop_id_object = tools.list_to_dict(shops, 'shop_id')

    all_goods = loop.run_until_complete(Goods.findAll())
    # all_goods = loop.run_until_complete(Goods.findAll('shop_id=?', shop_id))
    goods_id_object = tools.list_to_dict(all_goods, "goods_id")
    print("商品总数%s" % len(all_goods))

    goods_tmp = loop.run_until_complete(Goods_Tmp.findAll())
    goods_id_tmp = tools.list_to_dict(goods_tmp, "goods_id")

    # 初始化
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    global_goods_ids = []
    q_goods = queue.Queue(maxsize=30000)
    q_goods_insert = queue.Queue(maxsize=30000)
    q_goods_item = queue.Queue(maxsize=30000)
    q_goods_tmp = queue.Queue(maxsize=30000)

    q_stop = queue.Queue(maxsize=10)
    c1 = consumer.Consumer(1, q_goods, q_stop, event, lock, 'goods_update', loop)
    c1.daemon = True
    c1.start()
    c1_1 = consumer.Consumer(1_1, q_goods_insert, q_stop, event, lock, 'goods_insert', loop)
    c1_1.daemon = True
    c1_1.start()
    c2 = consumer.Consumer(2, q_goods_item, q_stop, event, lock, 'goods_item', loop)
    c2.daemon = True
    c2.start()
    c3 = consumer.Consumer(3, q_goods_tmp, q_stop, event, lock, 'goods_tmp', loop)
    c3.daemon = True
    c3.start()

    # for i in range(900):
    #     #     pc = shop_producer_consumer.Producer(i, q_datas, q_goods,q_goods_insert, q_goods_item, q_goods_tmp, event,
    #     #                                         goods_id_object, goods_id_tmp, cids)
    #     #     pc.daemon = True
    #     #     pc.start()
    for i in range(300):
        p = shop_producer.Producer(i, q_task, q_goods, q_goods_insert, q_goods_item, q_goods_tmp, event,
                                   global_goods_ids, goods_id_object, goods_id_tmp, cids)
        p.start()

    q_task.join()
    q_goods.join()
    q_goods_insert.join()
    q_goods_item.join()
    q_goods_tmp.join()
    q_stop.join()
    print("总共抓取了%s商品" % len(global_goods_ids))
    print("主程序结束")
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))
