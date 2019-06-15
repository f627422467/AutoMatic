import threading
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods, Goods_Item, Goods_Tmp
from Models.Categorys import Category_Cid
import datetime
import asyncio
from config import configs
import tools
import test
import time


class Consumer(threading.Thread):
    def __init__(self, name, task, queue, event):
        threading.Thread.__init__(self)
        self.name = "处理者" + str(name)
        self.task = task
        self.queue = queue
        self.event = event

    def run(self):
        while True:
            # 判断栈是否为空
            if self.task.empty() or self.queue.full():
                # 栈空 线程进入等待
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                # 判断栈是否已满，为满则在向栈取数据后，则将Flag设置为True,
                # 唤醒前所有在等待的生产者线程
                if self.task.full() or self.queue.empty():
                    item = self.task.get()
                    # 包装item
                    item += "TEST"
                    # time.sleep(1)
                    self.queue.put(item)
                    print("%s数据：%s" % (self.name, str(item)))
                    self.event.set()
                else:
                    # 未满 向栈添加数据
                    # self.lock.acquire()
                    item = self.task.get()
                    # 包装item
                    item += "TEST"
                    # time.sleep(1)
                    self.queue.put(item)
                    print("%s数据：%s" % (self.name, str(item)))
                    # self.lock.release()
                    # self.event.set()
                self.task.task_done()
