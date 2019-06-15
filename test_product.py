from multiprocessing import Process,JoinableQueue
import time

def producer(q,name,food):
    """
    生产者
    :param q: 队列
    :param name:
    :param food:
    :return:
    """
    for i in range(2):
        res = '%s,%s' %(food,i)
        time.sleep(1) # 生产food得有个过程，就先让睡一会
        print('生产者[%s] 生产了 [%s]' % (name, res))
        q.put(res)
    q.join()  # 等到消费者把自己放入队列中的所有的数据都取走之后，生产者才结束



def consumer(q,name):
    while True:
        res = q.get()
        if res is None:break
        time.sleep(2)
        print('消费者[%s]吃了[%s]' % (name,res) )
        q.task_done() # 发送信号给q.join()，说明已经从队列中取走一个数据并处理完毕了


if __name__ == '__main__':
    # 容器
    q=JoinableQueue()
    # 生产者
    p1 = Process(target=producer, args=(q, 'egon1', '包子'))
    p2 = Process(target=producer,args=(q,'egon2','饺子'))
    p3 = Process(target=producer,args=(q,'egon3','玉米'))

    # 消费者
    c1 = Process(target=consumer,args=(q,'alex1',))
    c2 = Process(target=consumer, args=(q, 'alex2',))

    pl = [p1,p2,p3]
    cl = [c1,c2]
    for p in pl:
        p.start()

    for c in cl:
        c.daemon = True  # 设置守护进程，主进程结束后，守护进程跟着结束
        c.start()

    for p in pl:
        p.join()
        # 1、主进程等生产者p1、p2、p3结束
        # 2、而p1、p2、p3是在消费者把所有数据都取干净之后才会结束
        # 3、所以一旦p1、p2、p3结束了，证明消费者也没必要存在了，应该随着主进程一块死掉，因而需要将生产者们设置成守护进程
    print('主进程结束')
