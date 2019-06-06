
import tools
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods,Goods_Item,Goods_Tmp
import asyncio
from config import configs
import datetime
from time import time
from Models.Categorys import Categorys,Category_Cid


async def check_shop(shop_id):
    shop_url = 'https://haohuo.snssdk.com/views/shop/index?id=' + shop_id
    shop = await Shop.findAll('shop_id=?', [shop_id])
    if len(shop) == 0:
        shop = Shop(shop_id=shop_id, shop_url=shop_url)
        shop.id = await shop.save()
        return shop
    return shop[0]


async def parse_page(json, shop_id,cids, goods_id_object):
    items = json.get('data').get('list')
    for item in items:
        sell_num = item.get('sell_num')
        if sell_num < 10:
            continue
        goods_id = item.get('product_id')
        goods_price = item.get('goods_price')
        goods_name = item.get('goods_name')
        cid = item.get('cid')
        if not cids.__contains__(cid):
            cid = item.get('second_cid')
        goods_picture_url = item.get('image')
        goods_url = 'https://haohuo.snssdk.com/views/product/item?id=' + goods_id
        is_add = False
        if goods_id_object.keys().__contains__(goods_id):
            #修改
            goods = goods_id_object.get(goods_id)
            time_now = datetime.datetime.now().strftime("%Y-%m-%d")
            time_last_edit = goods.edit_time.strftime("%Y-%m-%d")
            if sell_num < goods.sell_num:
                if time_now != time_last_edit:
                    goods.add_num = 0
                goods.edit_time = datetime.datetime.now()
                return
            if goods.item_last_sell_num is None:
                goods.item_last_sell_num = goods.sell_num
            # 较上次增量
            add_num = sell_num - goods.sell_num
            goods.goods_price = goods_price
            goods.sell_num = sell_num
            goods.cid = cid
            if time_now == time_last_edit:
                goods.add_num = goods.add_num + add_num
            else:
                goods.add_num = 0
            goods.edit_time = datetime.datetime.now()
            item_add_num = sell_num - goods.item_last_sell_num
            if item_add_num > 100:
                goods.item_last_sell_num = sell_num
            await goods.update()
            # goods_id_object.__delitem__(goods_id)
        else:
            #新增
            is_add = True
            item_add_num = 0
            goods = Goods()
            goods.shop_id = shop_id
            goods.goods_id = goods_id
            goods.cid = cid
            goods.goods_price = goods_price
            goods.goods_name = goods_name
            goods.goods_url = goods_url
            goods.goods_picture_url = goods_picture_url
            goods.sell_num = sell_num
            goods.item_last_sell_num = sell_num
            goods.id = await goods.save()
        if is_add or item_add_num >= 100:
            goods_item = Goods_Item()
            goods_item.goods_id = goods.id
            goods_item.sell_num = sell_num
            goods_item.add_num = item_add_num
            await goods_item.save()

        if is_add or goods.add_num > 0:
            await Goods_Tmp.del_by('goods_id=?',goods.id)
            tmp = Goods_Tmp()
            tmp.goods_id = goods.id
            tmp.add_num = goods.add_num
            tmp.edit_time = datetime.datetime.now()
            await tmp.save()

async def execOnPage(page,shopid,shop_id,goods_id_object,cids,semaphore):
    async with semaphore:
        # json = tools.get_page(shop_id, page)
        # print("%s ---前" % shop_id)
        json = await tools.aiohttp_get_page(shop_id, page)
        # print("%s ---后" % shop_id)
        if json is None:
            return
        if json.get('data') is None:
            return
        await parse_page(json, shopid,cids, goods_id_object)
            # print(u"抓取店铺%s第%s页 " % (shop_id, page))


async def exec(shop_id,cids,semaphore):
    async with semaphore:
        print(u"开始抓取店铺%s:%s" % (shop_id,datetime.datetime.now()))
        shop = await check_shop(shop_id)
        already_goods = await Goods.findAll('shop_id=?',shop.id)
        goods_id_object = tools.list_to_dict(already_goods,'goods_id')
        index = 0
        for page in range(0, 10000):
            json = await tools.aiohttp_get_page(shop_id, page)
            if json is None:
                break
            if json.get('data') is None:
                break
            await parse_page(json, shop.id,cids, goods_id_object)
            index += 1
        print(u"抓取店铺%s完成:%s，总页数：%s" % (shop_id,datetime.datetime.now(),index))


async def exec_shop(shop_id,shopid,cids,goods_id_object):
     taskDict_1 = {}
     tasks_1 = []
     key_1 = 0
     #服务器带宽太小，压力承受不住，1
     semaphore_1 = asyncio.Semaphore(3)
     for page in range(0, 10000):
         if page != 0 and page % 500 == 0:
             taskDict_1["%s" % key_1] = tasks_1
             tasks_1 = []
             key_1 += 1
         if page != 0 and page % 50 == 0:
             json = await tools.aiohttp_get_page(shop_id, page)
             if json is None or json.get('data') is None:
                 break
         tasks_1.append(asyncio.ensure_future(execOnPage(page, shopid, shop_id,cids, goods_id_object,semaphore_1)))
     taskDict_1["%s" % key_1] = tasks_1
     for taskKey_1 in taskDict_1:
         tempTasks_1 = taskDict_1[taskKey_1]
         await asyncio.wait(tempTasks_1)


#按店铺抓取
if __name__ == '__main__':
    start = time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    # shops = loop.run_until_complete(Shop.findAll())
    category_cids = loop.run_until_complete(Category_Cid.findAll())
    cids = []
    for category_cid in category_cids:
        if not cids.__contains__(category_cid.cid):
            cids.append(category_cid.cid)
    #shops = loop.run_until_complete(Shop.findAll("create_time>?","2019-06-03 09:30:32"))
    tasks = []
    #服务器15，带宽正合适
    semaphore = asyncio.Semaphore(500)
    with open(r'shop_ids.txt', 'r', encoding='utf-8') as f:
        shop_ids = f.readlines()
        for shop_id in shop_ids:
            shop_id = shop_id.strip('\n')
        # for shop in shops:
        #     shop_id = shop.shop_id
            # shop_id = shop
            tasks.append(asyncio.ensure_future(exec(shop_id,cids,semaphore)))
    dones, pendings = loop.run_until_complete(asyncio.wait(tasks))
    print("完成的任务数：%s" % len(dones))
    end = time()
    print('Cost {} seconds'.format(end - start))

