import threading
import random
import tools
import asyncio
import time
import datetime
from Models.Goods import Goods, Goods_Item, Goods_Tmp
from Models.Shop import Shop_Number


class Producer(threading.Thread):
    def __init__(self, name, task, q_number, event, global_goods_ids,shop_key):
        threading.Thread.__init__(self)
        self.name = "生产者" + str(name)
        self.task = task
        self.q_number = q_number
        self.event = event
        self.global_goods_ids = global_goods_ids
        self.shop_key = shop_key

    def run(self):
        loop = asyncio.new_event_loop()
        while True:
            if self.task.empty():
                break
            goods_id = self.task.get()
            # print(u"开始生产%s" % goods_id)
            item = loop.run_until_complete(tools.get_goods_by_id(goods_id))
            if not item or not item.get('data'):
                self.task.task_done()
                continue
            if not item.get('data').get('name') or item.get('data').get('name') == '':
                self.task.task_done()
                continue
            if self.global_goods_ids.__contains__(goods_id):
                self.task.task_done()
                continue
            self.global_goods_ids.append(goods_id)
            item = item.get('data')
            shop_id = item.get('shop_id')
            shop_tel = item.get('shop_tel')
            key = '%s %s' % (shop_id, shop_tel)
            if self.shop_key.__contains__(key):
                self.task.task_done()
                continue
            self.shop_key.append(key)
            # 判断栈是否已经满
            if self.q_number.full():
                print("队列已满，总数%s" % self.q_number.qsize())
                # 栈满 线程进入等待
                self.event.set()
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                is_empty = False
                if self.q_number.empty():
                    is_empty = True
                self.do_entitry(item)
                self.task.task_done()
                if is_empty:
                    self.event.set()
                    # print(" %s 唤起其他人" % self.name)
        print(self.name + "结束")

    def do_entitry(self, item):
        shop_id = item.get('shop_id')
        shop_name = item.get('shop_name')
        shop_tel = item.get('shop_tel')
        shop_number = Shop_Number()
        shop_number.shop_id = shop_id
        shop_number.shop_name = shop_name
        shop_number.shop_tel = shop_tel
        self.q_number.put(shop_number)


