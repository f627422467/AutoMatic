from ByTime import time_producer
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
import sys
import tools

async def exec_not_sell(goods_id,semaphore):
    async with semaphore:
        goods = await Goods.find_one('goods_id=?', goods_id)
        if goods:
            goods.is_selling = False
            goods.edit_time = datetime.datetime.now()
            await goods.update()


async def exec_data(item, cids, semaphore,goods):
    async with semaphore:
        sell_num = item.get('sell_num')
        goods_id = item.get('product_id')
        if not goods_id:
            return
        shop_id = item.get('shop_id')
        goods_price = item.get('discount_price')/100
        goods_name = item.get('name')
        cid = item.get('third_cid')
        if not cids.__contains__(cid):
            cid = item.get('second_cid')
        goods_picture_url = item.get('img')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        # goods = await Goods.find_one('goods_id=?', goods_id)
        if goods:
            # 修改
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            # 较上次增量
            sell_num_old = goods.sell_num
            add_num = sell_num - sell_num_old
            goods.shop_id = shop_id
            goods.cid = cid
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.goods_price = goods_price
            if time_now != time_last_edit:
                goods.add_num = 0
            elif goods.add_num < 0:
                goods.add_num = add_num
            else:
                goods.add_num = goods.add_num + add_num
            if goods.add_num < 0:
                print(item)
                print("goods_id:%s;add_num:%s;sell_num:%s;last_sell_num:%s;last:%s;" % (goods.goods_id,add_num,sell_num,sell_num_old,goods.add_num))
            goods.sell_num = sell_num
            if goods.item_last_sell_num is None:
                goods.item_last_sell_num = goods.sell_num
            goods.edit_time = datetime.datetime.now()

            item_add_num = sell_num - goods.item_last_sell_num
            if item_add_num > 100:
                goods.item_last_sell_num = sell_num
            await goods.update()
        else:
            raise Exception("出错！数据库中没有查询到相应值")
        if item_add_num >= 100:
            goods_item = Goods_Item()
            goods_item.goods_id = goods.id
            goods_item.sell_num = sell_num
            goods_item.add_num = item_add_num
            await goods_item.save()
        if goods.add_num > 0:
            await Goods_Tmp.del_by('goods_id=?', goods.id)
            tmp = Goods_Tmp()
            tmp.goods_id = goods.id
            tmp.add_num = goods.add_num
            tmp.sell_num = goods.sell_num
            tmp.edit_time = datetime.datetime.now()
            await tmp.save()


# 按照给定时间更新
if __name__ == '__main__':

    query_time = str(sys.argv[1])
    # query_time = '2019-06-11 00:01:00'
    print(query_time)
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    goods = loop.run_until_complete(Goods.findAll('edit_time<? and is_selling=?', [query_time,True]))
    q_goods = queue.Queue(maxsize=0)
    for good in goods:
        q_goods.put_nowait(good.goods_id)
    print("商品总数%s" % q_goods.qsize())

    goods_id_object = tools.list_to_dict(goods, "goods_id")

    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)
    # 初始化
    q_data = queue.Queue(maxsize=30000)
    global_goods_ids = []
    global_not_goods_ids = []
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    for i in range(100):
        p = time_producer.Producer(i, q_goods, q_data, event, global_goods_ids,global_not_goods_ids)
        p.start()

    semaphore = asyncio.Semaphore(500)
    while True:
        if q_data.empty():
            # 栈空 线程进入等待
            event.wait(30)
            if q_goods.empty() and q_data.empty():
                time.sleep(10)
                if q_goods.empty() and q_data.empty():
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
                    goods = goods_id_object.get(item.get('product_id'))
                    tasks.append(asyncio.ensure_future(exec_data(item, cids, semaphore,goods)))
                    q_data.task_done()
                if len(tasks) > 0:
                    print("开始任务：%s，数量：%s" % (datetime.datetime.now(), len(tasks)))
                    dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
                    print("完成的任务数：%s,时间点：%s" % (len(dones), datetime.datetime.now()))
                    print("当前对列数：%s" % q_data.qsize())
                    event.set()
            else:
                tasks = []
                for i in range(q_data.qsize()):
                    item = q_data.get()
                    goods = goods_id_object.get(item.get('product_id'))
                    tasks.append(asyncio.ensure_future(exec_data(item, cids, semaphore,goods)))
                    q_data.task_done()
                if len(tasks) > 0:
                    print("开始任务：%s，数量：%s" % (datetime.datetime.now(), len(tasks)))
                    dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
                    print("完成的任务数：%s,时间点：%s" % (len(dones), datetime.datetime.now()))
                    print("当前对列数：%s" % q_data.qsize())
                    event.set()
    q_data.join()

    if global_not_goods_ids:
        print("有下架的商品，数量%s" % len(global_not_goods_ids))
        tasks = []
        for goods_id in global_not_goods_ids:
            tasks.append(asyncio.ensure_future(exec_not_sell(goods_id,semaphore)))
        print("开始任务：%s，数量：%s" % (datetime.datetime.now(), len(tasks)))
        dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
        print("完成的任务数：%s,时间点：%s" % (len(dones), datetime.datetime.now()))

    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))
    sys.exit()

