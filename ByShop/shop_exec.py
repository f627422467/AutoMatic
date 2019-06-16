import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from ByShop import shop_producer, shop_producer_consumer
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


async def check_shop(shop_id, shop_id_object):
    shop_url = 'https://haohuo.snssdk.com/views/shop/index?id=' + shop_id
    shop = shop_id_object.get(shop_id)
    if not shop:
        shop = Shop(shop_id=shop_id, shop_url=shop_url)
        shop.id = await shop.save()
        return shop
    return shop


async def exec_data(item, cids, semaphore, shop_id_object, goods):
    async with semaphore:
        goods_id = item.get('product_id')
        if not goods_id:
            return
        sell_num = int(item.get('sell_num'))
        shop_id = item.get('shop_id')
        await check_shop(shop_id, shop_id_object)
        goods_price = item.get('discount_price') / 100
        goods_name = item.get('name')
        cid = item.get('third_cid')
        if not cids.__contains__(cid):
            cid = item.get('second_cid')
        goods_picture_url = item.get('img')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        is_add = False
        # goods = await Goods.find_one('goods_id=?', goods_id)
        # goods = goods_id_object.get(goods_id)
        if goods:
            # 修改
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            # 较上次增量
            add_num = sell_num - goods.sell_num
            goods.shop_id = shop_id
            goods.cid = cid
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.goods_price = goods_price
            if time_now != time_last_edit:
                if add_num >= 0:
                    goods.add_num = 0 + add_num
                else:
                    goods.add_num = 0
            elif add_num >= 0:
                goods.add_num = goods.add_num + add_num
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


# 按照既有店铺更新商品
if __name__ == '__main__':
    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    shops = loop.run_until_complete(Shop.findAll())
    # shops = loop.run_until_complete(Shop.findAll('shop_id=?', 'hmSuxrl'))
    q_task = queue.Queue(maxsize=0)
    for shop in shops:
        q_task.put(shop)
    print("店铺总数%s" % q_task.qsize())

    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)

    shop_id_object = tools.list_to_dict(shops, 'shop_id')

    all_goods = loop.run_until_complete(Goods.findAll())
    goods_id_object = tools.list_to_dict(all_goods, "goods_id")

    goods_tmp = loop.run_until_complete(Goods_Tmp.findAll())
    goods_id_tmp = tools.list_to_dict(goods_tmp, "goods_id")

    # 初始化
    event = threading.Event()
    lock = threading.Lock()

    if event.isSet:
        event.clear()

    global_goods_ids = []
    q_datas = queue.Queue(maxsize=30000)
    q_goods = queue.Queue(maxsize=30000)
    q_goods_insert = queue.Queue(maxsize=30000)
    q_goods_item = queue.Queue(maxsize=30000)
    q_goods_tmp = queue.Queue(maxsize=30000)

    q_stop = queue.Queue(maxsize=10)
    c1 = consumer.Consumer(1, q_goods, q_stop, event, lock, 'goods_update', loop)
    c1.daemon = True
    c1_1 = consumer.Consumer(1_1, q_goods_insert, q_stop, event, lock, 'goods_insert', loop)
    c1_1.daemon = True
    c1.start()
    c2 = consumer.Consumer(2, q_goods_item, q_stop, event, lock, 'goods_item', loop)
    c2.daemon = True
    c2.start()
    c3 = consumer.Consumer(3, q_goods_tmp, q_stop, event, lock, 'goods_tmp', loop)
    c3.daemon = True
    c3.start()

    for i in range(900):
        p = shop_producer_consumer.Producer(i, q_datas, q_goods,q_goods_insert, q_goods_item, q_goods_tmp, event,
                                            goods_id_object, goods_id_tmp, cids)
        p.start()

    for i in range(200):
        p = shop_producer.Producer(i, q_task, q_datas, event, global_goods_ids)
        p.start()

    q_task.join()
    q_goods.join()
    q_goods_item.join()
    q_goods_tmp.join()
    q_stop.join()
    print("主程序结束")
