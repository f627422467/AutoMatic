import threading
import time

condition = threading.Condition()
products = 0


class Producer(threading.Thread):
    '''生产者'''
    ix = [0]  # 生产者实例个数

    # 闭包，必须是数组，不能直接 ix = 0
    def __init__(self, ix=0):
        super().__init__()
        self.ix[0] += 1
        self.setName('生产者' + str(self.ix[0]))

    def run(self):
        global condition, products

        while True:
            if condition.acquire():
                if products < 10:
                    products += 1;
                    print("{}：库存不足(10-)。我努力生产了1件产品，现在产品总数量 {}".format(self.getName(), products))
                    condition.notify()
                else:
                    print("{}：库存充足(10+)。让我休息会儿，现在产品总数量 {}".format(self.getName(), products))
                    condition.wait();
                condition.release()
                time.sleep(2)


class Consumer(threading.Thread):
    '''消费者'''
    ix = [0]  # 消费者实例个数

    # 闭包，必须是数组，不能直接 ix = 0
    def __init__(self):
        super().__init__()
        self.ix[0] += 1
        self.setName('消费者' + str(self.ix[0]))

    def run(self):
        global condition, products

        while True:
            if condition.acquire():
                if products > 1:
                    products -= 1
                    print("{}：我消费了1件产品，现在产品数量 {}".format(self.getName(), products))
                    condition.notify()
                else:
                    print("{}：只剩下1件产品，我停止消费。现在产品数量 {}".format(self.getName(), products))
                    condition.wait();
                condition.release()
                time.sleep(2)


if __name__ == "__main__":
    for i in range(2):
        p = Producer()
        p.start()

    for i in range(10):
        c = Consumer()
        c.start()