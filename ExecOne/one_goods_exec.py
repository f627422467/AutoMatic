import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
sys.path.append("/opt/AutoMatic/")
import tools
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods, Goods_Item, Goods_Tmp
import asyncio
from config import configs
import functools
import sys
import datetime


async def parse_page(goods_id):
    # item = await tools.get_goods_by_id(goods_id)
    item = tools.get_goods(goods_id)
    print(item)
    if not item:
        return
    if not item.get('data'):
        return
    product_id = item.get('data').get('product_id')
    if not product_id:
        return
    try:
        sell_num = int(item.get('data').get('sell_num'))
    except Exception as e:
        print("转化销量失败：%s" % e)
        return
    goods = await Goods.find_one('goods_id=?', goods_id)
    if goods:
        # 修改
        time_now = datetime.datetime.now().strftime("%Y-%m-%d")
        time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
        # 较上次增量
        add_num = sell_num - goods.sell_num
        if time_now != time_last_edit:
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


async def exec(goods_id):
    print(u"开始抓取商品%s:%s" % (goods_id, datetime.datetime.now()))
    try:
        await parse_page(goods_id)
    except Exception as e:
        print(u"抓取商品%s出错，原因：%s " % (goods_id, e))
    print(u"抓取商品%s完成:%s" % (goods_id, datetime.datetime.now()))


async def init(loop, goods_id):
    await orm.create_pool(loop=loop, **configs.db)
    await exec(goods_id)


def done_callback(loop, futu):
    if loop is not None:
        loop.stop()


# 页面手动更新单个产品
if __name__ == '__main__':
    # goods_id = str(sys.argv[1])
    # print(goods_id)
    goods_id = str(3336675539900574025)
    # goods_id = str(3351526115033413385)
    loop = asyncio.get_event_loop()
    futus = asyncio.gather(init(loop, goods_id))
    futus.add_done_callback(functools.partial(done_callback, loop))
    loop.run_forever()
