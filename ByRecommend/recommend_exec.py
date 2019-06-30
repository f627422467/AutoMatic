import sys
sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from ByRecommend import recommend_producer
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

async def check_shop(shop_id):
    shop_url = 'https://haohuo.snssdk.com/views/shop/index?id=' + shop_id
    shop = await Shop.findAll('shop_id=?', [shop_id])
    if len(shop) == 0:
        shop = Shop(shop_id=shop_id, shop_url=shop_url)
        shop.id = await shop.save()
        return shop
    return shop[0]


async def exec_data(item, cids, semaphore):
    async with semaphore:
        goods_id = item.get('product_id')
        if not goods_id:
            return
        sell_num = tools.get_sell_num(item.get('sell_num'))
        shop_id = item.get('shop_id')
        await check_shop(shop_id)
        goods_price = item.get('discount_price') / 100
        goods_name = item.get('name')
        cid = item.get('cid')
        if not cids.__contains__(cid):
            cid = item.get('second_cid')
        goods_picture_url = item.get('img')
        biz_type = item.get('biz_type')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        is_add = False
        goods = await Goods.find_one('goods_id=?', goods_id)
        if goods:
            # 修改
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            # 较上次增量
            add_num = sell_num - goods.sell_num
            goods.shop_id = shop_id
            goods.cid = cid
            goods.biz_type = biz_type
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.goods_price = goods_price
            if time_now != time_last_edit:
                goods.add_num = 0
            elif add_num >= 0:
                goods.add_num = goods.add_num + add_num
            if add_num < 0:
                return
            goods.sell_num = sell_num
            if goods.item_last_sell_num is None:
                goods.item_last_sell_num = goods.sell_num
            goods.edit_time = datetime.datetime.now()

            item_add_num = sell_num - goods.item_last_sell_num
            if item_add_num > 100:
                goods.item_last_sell_num = sell_num
            await goods.update()
        else:
            # 新增
            is_add = True
            item_add_num = 0
            goods = Goods()
            goods.shop_id = shop_id
            goods.goods_id = goods_id
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.goods_price = goods_price
            goods.cid = cid
            goods.biz_type = biz_type
            goods.add_num = 0
            goods.sell_num = sell_num
            goods.item_last_sell_num = sell_num
            goods.id = await goods.save()
            if goods.id == 0:
                is_add = False
        if is_add or item_add_num >= 100:
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


# 首页精选推荐
if __name__ == '__main__':

    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))

    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)
    # 初始化
    q_data = queue.Queue(maxsize=30000)
    global_goods_ids = []
    global_page = []
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    for i in range(100):
        p = recommend_producer.Producer(i, q_data, event, global_page, global_goods_ids)
        p.start()

    semaphore = asyncio.Semaphore(500)
    while True:
        if q_data.empty():
            # 栈空 线程进入等待
            event.wait(30)
            if q_data.empty():
                time.sleep(10)
                if q_data.empty():
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
                    tasks.append(asyncio.ensure_future(exec_data(item, cids, semaphore)))
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
                    tasks.append(asyncio.ensure_future(exec_data(item, cids, semaphore)))
                    q_data.task_done()
                if len(tasks) > 0:
                    print("开始任务：%s，数量：%s" % (datetime.datetime.now(), len(tasks)))
                    dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
                    print("完成的任务数：%s,时间点：%s" % (len(dones), datetime.datetime.now()))
                    print("当前对列数：%s" % q_data.qsize())
                    event.set()
    q_data.join()
    end = datetime.datetime.now()
    print('Cost {} seconds'.format(end - start))
