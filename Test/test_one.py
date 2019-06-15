from Test import test_producer, test_producer_consumer, test_consumer
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

    q_task = queue.Queue(maxsize=0)
    for i in range(10):
        q_task.put(i)

    # 初始化
    q_data = queue.Queue(maxsize=30000)
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    for i in range(3):
        p = test_producer.Producer(i, q_task, q_data, event)
        p.start()

    q_entiry = queue.Queue(maxsize=30000)

    for i in range(1):
        pc = test_producer_consumer.Consumer(i, q_data, q_entiry, event)
        pc.daemon = True
        pc.start()

    q_stop = queue.Queue(maxsize=10)
    c = test_consumer.Consumer(i, q_entiry,q_stop,event)
    c.daemon = True
    c.start()

    q_task.join()
    q_data.join()
    q_entiry.join()
    q_stop.join()
    print("主程序结束")
