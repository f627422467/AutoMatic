import threading
import random
import tools
import asyncio
import time


class Producer(threading.Thread):
    def __init__(self, name, task, queue, event,global_goods_ids,global_not_goods_ids):
        threading.Thread.__init__(self)
        self.name = "生产者" + str(name)
        self.task = task
        self.queue = queue
        self.event = event
        self.global_goods_ids = global_goods_ids
        self.global_not_goods_ids = global_not_goods_ids

    def run(self):
        loop = asyncio.new_event_loop()
        while True:
            if self.task.empty():
                break
            goods_id = self.task.get()
            print(u"开始生产%s" % goods_id)
            item = loop.run_until_complete(tools.get_goods_by_id(goods_id))
            if not item or not item.get('data'):
                continue
            if not item.get('data').get('name') or item.get('data').get('name') == '':
                self.global_not_goods_ids.append(goods_id)
                continue
            if self.global_goods_ids.__contains__(goods_id):
                continue
            self.global_goods_ids.append(goods_id)
            item = item.get('data')
            # 判断栈是否已经满
            if self.queue.full():
                print("队列已满，总数%s" % self.queue.qsize())
                # 栈满 线程进入等待
                self.event.set()
                self.event.wait()
                # 线程唤醒后将flag设置为False
                if self.event.isSet():
                    self.event.clear()
            else:
                # 未满 向栈添加数据
                is_empty = self.queue.empty()
                self.queue.put(item)
                # print("%s数据：%s" % (self.name, str(item)))
                self.task.task_done()
                if is_empty:
                    # 将Flag设置为True
                    self.event.set()
        print(self.name + "结束")


