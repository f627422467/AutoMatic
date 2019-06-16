import threading
import random
import tools
import asyncio
import time
import datetime
from Models.Goods import Goods, Goods_Item, Goods_Tmp


class Producer(threading.Thread):
    def __init__(self, name, task, q_goods, q_goods_item, q_goods_tmp, event, global_goods_ids,
                 goods_id_object, goods_id_tmp, cids):
        threading.Thread.__init__(self)
        self.name = "生产者" + str(name)
        self.task = task
        self.q_goods = q_goods
        self.q_goods_item = q_goods_item
        self.q_goods_tmp = q_goods_tmp
        self.event = event
        self.global_goods_ids = global_goods_ids
        self.goods_id_object = goods_id_object
        self.goods_id_tmp = goods_id_tmp
        self.cids = cids

    def run(self):
        loop = asyncio.new_event_loop()
        while True:
            if self.task.empty():
                break
            shop_id = self.task.get().shop_id
            print("开始抓取店铺%s" % shop_id)
            # TODO
            self.task.task_done()
            page = 0
            while True:
                json = loop.run_until_complete(tools.get_first_goods_by_shop(shop_id, page))
                if json is None:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                if json.get('data') is None or len(json.get('data')) <= 0:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                if json.get('data').get('list') is None or len(json.get('data').get('list')) <= 0:
                    print("抓取店铺%s完毕，总页数：%s" % (shop_id, page))
                    break
                items = json.get('data').get('list')
                for item in items:
                    sell_num = item.get('sell_num')
                    goods_id = item.get('product_id')
                    if sell_num < 1:
                        continue
                    if self.global_goods_ids.__contains__(goods_id):
                        continue
                    self.global_goods_ids.append(goods_id)

        print(self.name + "结束")

    def do_entitry(self, item):
        goods_id = item.get('product_id')
        if not goods_id:
            return
        goods = self.goods_id_object.get(goods_id)
        sell_num = int(item.get('sell_num'))
        shop_id = item.get('shop_id')
        goods_price = item.get('discount_price') / 100
        goods_name = item.get('name')
        cid = item.get('third_cid')
        if not self.cids.__contains__(cid):
            cid = item.get('second_cid')
        goods_picture_url = item.get('img')
        biz_type = item.get('biz_type')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        if goods:
            # 修改
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            # 较上次增量
            sell_num_old = goods.sell_num
            add_num = sell_num - sell_num_old
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
            if goods.add_num < 0:
                print(item)
                print("goods_id:%s;add_num:%s;sell_num:%s;last_sell_num:%s;last:%s;" % (
                    goods.goods_id, add_num, sell_num, sell_num_old, goods.add_num))
            goods.sell_num = sell_num
            if goods.item_last_sell_num is None:
                goods.item_last_sell_num = goods.sell_num
            goods.edit_time = datetime.datetime.now()

            item_add_num = sell_num - goods.item_last_sell_num
            if item_add_num > 100 or item_add_num < 0:
                goods.item_last_sell_num = sell_num
            # await goods.update()
            self.q_goods.put(goods)
            print("goods 队列：%s" % self.q_goods.qsize())
        else:
            raise Exception("出错！数据库中没有查询到相应值")
        if item_add_num >= 100:
            goods_item = Goods_Item()
            goods_item.goods_id = goods.id
            goods_item.sell_num = sell_num
            goods_item.add_num = item_add_num
            # await goods_item.save()
            self.q_goods_item.put(goods_item)
            print("q_goods_item 队列：%s" % self.q_goods_item.qsize())
        if goods.add_num > 0:
            tmp = self.goods_id_tmp.get(goods.id)
            if not tmp:
                tmp = Goods_Tmp()
            # await Goods_Tmp.del_by('goods_id=?', goods.id)
            tmp.goods_id = goods.id
            tmp.add_num = goods.add_num
            tmp.sell_num = goods.sell_num
            tmp.edit_time = datetime.datetime.now()
            # await tmp.save()
            self.q_goods_tmp.put(tmp)
            print("q_goods_tmp 队列：%s" % self.q_goods_tmp.qsize())

    def exec_not_sell(self, goods_id):
        goods = self.goods_id_object.get(goods_id)
        if goods:
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            if time_now != time_last_edit:
                goods.add_num = 0
            goods.is_selling = False
            # goods.add_num = 0
            goods.edit_time = datetime.datetime.now()
            self.q_goods.put(goods)
            print("goods 队列：%s" % self.q_goods.qsize())
