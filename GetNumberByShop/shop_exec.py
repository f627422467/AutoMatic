import sys
sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from GetNumberByShop import shop_producer
import consumer
import threading
import queue
import asyncio
from ORM import orm
from Models.Shop import Shop,Shop_Number
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
    # shops = loop.run_until_complete(Shop.findAll('shop_id=?', 'hmSuxrl'))
    q_shops = queue.Queue(maxsize=0)
    for shop in shops:
        q_shops.put_nowait(shop)
    print("店铺总数%s" % q_shops.qsize())

    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)

    shop_id_object = tools.list_to_dict(shops, 'shop_id')

    all_goods = loop.run_until_complete(Goods.findAll())
    goods_id_object = tools.list_to_dict(all_goods, "goods_id")

    # 初始化
    q_data = queue.Queue(maxsize=30000)
    global_goods_ids = []
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    for i in range(600):
        p = shop_producer.Producer(i, q_shops, q_data, event, global_goods_ids)
        p.start()

    semaphore = asyncio.Semaphore(500)
    while True:
        if q_data.empty():
            # 栈空 线程进入等待
            event.wait(30)
            if q_shops.empty() and q_data.empty():
                time.sleep(10)
                if q_shops.empty() and q_data.empty():
                    print("退出")
                    break
            # 线程唤醒后将flag设置为False
            if event.isSet():
                event.clear()
        else:
            if q_data.full():
                tasks = []
                for i in range(q_data.qsize()):
                    item = q_data.get()
                    shop_id = item.get('shop_id')
                    shop_name = item.get('shop_name')
                    shop_tel = item.get('shop_tel')
                    shop_number = Shop_Number()
                    shop_number.shop_id = shop_id
                    shop_number.shop_name = shop_name
                    shop_number.shop_tel = shop_tel
                    tasks.append(shop_number)
                loop.run_until_complete(Shop_Number.batch_insert(tasks))
                event.set()
            else:
                tasks = []
                for i in range(q_data.qsize()):
                    item = q_data.get()
                    shop_id = item.get('shop_id')
                    shop_name = item.get('shop_name')
                    shop_tel = item.get('shop_tel')
                    shop_number = Shop_Number()
                    shop_number.shop_id = shop_id
                    shop_number.shop_name = shop_name
                    shop_number.shop_tel = shop_tel
                    tasks.append(shop_number)
                loop.run_until_complete(Shop_Number.batch_insert(tasks))
                event.set()
    q_data.join()
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))
    sys.exit()
