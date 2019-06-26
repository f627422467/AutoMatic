import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from GetNumberByShop import number_producer
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


def exec(goods, loop):

    print("子任务执行完毕")


if __name__ == '__main__':

    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    goods = loop.run_until_complete(Goods.findAll('biz_type=?', '1'))
    q_task = queue.Queue(maxsize=0)
    for good in goods:
        q_task.put(good.goods_id)
    print("商品总数%s" % q_task.qsize())

    # 初始化
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    global_goods_ids = []
    shop_key = []

    q_number = queue.Queue(maxsize=0)

    q_stop = queue.Queue(maxsize=10)
    c1 = consumer.Consumer(1, q_number, q_stop, event, lock, 'shop_number', loop)
    c1.daemon = True
    c1.start()

    for i in range(100):
        p = number_producer.Producer(i, q_task, q_number, event, global_goods_ids,shop_key)
        p.start()

    q_task.join()
    q_stop.join()

    print("主程序结束")
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))
