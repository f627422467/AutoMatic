import threading
import random
import tools
import asyncio
import time


class Producer(threading.Thread):
    def __init__(self, name, q_goods, queue, event, global_goods_ids):
        threading.Thread.__init__(self)
        self.name = "生产者" + str(name)
        self.queue = queue
        self.event = event
        self.q_goods = q_goods
        self.global_goods_ids = global_goods_ids

    def run(self):
        loop = asyncio.new_event_loop()
        while True:
            if self.q_goods.empty():
                self.event.set()
                break
            goods_id = self.q_goods.get()
            print(u"开始抓取商品%s" % goods_id)
            self.q_goods.task_done()
            item = loop.run_until_complete(tools.get_goods_by_id(goods_id))
            if not item or not item.get('data'):
                continue
            if not item.get('data').get('name') or item.get('data').get('name') == '':
                print("下架： %s" % goods_id)
                continue
            if self.global_goods_ids.__contains__(goods_id):
                continue
            self.global_goods_ids.append(goods_id)
            # 判断栈是否已经满
            if self.queue.full():
                print("队列已满，总数%s" % self.queue.qsize())
                # 栈满 线程进入等待
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                # 判断栈是否为空，为空则在向栈添加数据后，则将Flag设置为True,
                # 唤醒前所有在等待的消费者线程
                if self.queue.empty():
                    # 未满 向栈添加数据
                    self.queue.put(item.get('data'))
                    # print("生产数据：%s" + str(item))
                    # 将Flag设置为True
                    self.event.set()
                else:
                    # 未满 向栈添加数据
                    self.queue.put(item.get('data'))
                    # print("生产数据：%s" + str(item))
                    self.event.set()
        print(self.name + "结束")
