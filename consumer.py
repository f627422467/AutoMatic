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


class Consumer(threading.Thread):
    def __init__(self, i, q_shops, cids, queue, event, lock, loop):
        threading.Thread.__init__(self)
        self.name = "消费者" + str(i)
        self.q_shops = q_shops
        self.cids = cids
        self.queue = queue
        self.event = event
        self.lock = lock
        self.loop = loop

    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
        while True:
            # 判断栈是否为空
            if self.queue.empty():
                # 栈空 线程进入等待
                self.event.wait(10)
                # if self.q_shops.empty() and self.queue.empty():
                #     self.event.set()
                #     break
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                # 判断栈是否已满，为满则在向栈取数据后，则将Flag设置为True,
                # 唤醒前所有在等待的生产者线程
                if self.queue.full():
                    # # 未满 向栈添加数据
                    # # self.lock.acquire()
                    # data = self.queue.get()
                    # # 请求数据库
                    # self.loop.run_until_complete(self.exec_data(data))
                    # self.queue.task_done()
                    # # self.lock.release()
                    # # 将Flag设置为True
                    # self.event.set()

                    tasks = []
                    for i in range(self.queue.qsize() - 50):
                        item = self.queue.get()
                        tasks.append(asyncio.ensure_future(test.exec_data(item, self.cids)))
                        dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
                        print("完成的任务数：%s" % len(dones))
                        self.queue.task_done()
                    self.event.set()
                else:
                    if self.queue.qsize() >= 100:
                        tasks = []
                        for i in range(100):
                            item = self.queue.get()
                            tasks.append(asyncio.ensure_future(test.exec_data(item, self.cids)))
                            dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
                            print("完成的任务数：%s" % len(dones))
                            self.queue.task_done()
                    else:
                        # 未满 向栈添加数据
                        # self.lock.acquire()
                        item = self.queue.get()
                        tasks = []
                        tasks.append(asyncio.ensure_future(test.exec_data(item, self.cids)))
                        dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
                        print("完成的任务数：%s" % len(dones))
                        self.queue.task_done()
                        # self.lock.release()
        print(self.name + "结束")
