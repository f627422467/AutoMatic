
import tools
from ORM import orm
from Models.Goods import Goods,Goods_Item,Goods_Tmp
import asyncio
from config import configs
import datetime
from time import time
import sys

async def parse_page(goods):
    item = await tools.aiohttp_get_goods_by_id(good.goods_id)
    if not item or not item.get('data'):
        return
    if not item.get('data').get('name') or item.get('data').get('name') == '':
        return
    sell_num = item.get('data').get('sell_num')
    time_now = datetime.datetime.now().strftime("%Y-%m-%d")
    time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
    if sell_num <= 0 or sell_num < goods.sell_num:
        if time_now != time_last_edit:
            goods.add_num = 0
        goods.edit_time = datetime.datetime.now()
        await goods.update()
        return
    # 修改
    if goods.item_last_sell_num is None:
        goods.item_last_sell_num = goods.sell_num
    # 较上次增量
    add_num = sell_num - goods.sell_num
    goods.sell_num = sell_num
    if time_now == time_last_edit:
        goods.add_num = goods.add_num + add_num
    else:
        goods.add_num = 0
    goods.edit_time = datetime.datetime.now()
    item_add_num = sell_num - goods.item_last_sell_num
    if item_add_num > 100:
        goods.item_last_sell_num = sell_num
    await goods.update()
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
        tmp.edit_time = datetime.datetime.now()
        await tmp.save()


async def exec(good,semaphore):
    async with semaphore:
        print(u"开始抓取商品%s:%s" % (good.goods_id, datetime.datetime.now()))
        try:
            await parse_page(good)
        except Exception as e:
            print(u"抓取商品%s出错，原因：%s " % (good.goods_id, e))
        print(u"抓取商品%s完成:%s" % (good.goods_id, datetime.datetime.now()))


#按时间抓
if __name__ == '__main__':
    #query_time = str(sys.argv[1])
    #query_time = '2019-06-03 05:31:15'
    #print(query_time)
    start = time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    # goods = loop.run_until_complete(Goods.findAll('id in (select distinct goods_id from %s )' % tools.get_temp_table()))
    goods = loop.run_until_complete(Goods.find_inner(tools.get_temp_table(),'goods_id'))
    tasks = []
    #服务器15，带宽正合适
    semaphore = asyncio.Semaphore(500)
    for good in goods:
        tasks.append(asyncio.ensure_future(exec(good,semaphore)))
    dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
    print("完成的任务数：%s" % len(dones))
    end = time()
    print('Cost {} seconds'.format(end - start))

