import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
from ByTmp import tmp_producer
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
import json


async def check_shop(shop_id):
    if not shop_id:
        return
    shop_url = 'https://haohuo.snssdk.com/views/shop/index?id=' + shop_id
    shop = await Shop.findAll('shop_id=?', [shop_id])
    if len(shop) == 0:
        print("不存在%s,开始插入" % shop_id)
        shop = Shop(shop_id=shop_id, shop_url=shop_url)
        await shop.save()
    else:
        print("%s已存在" % shop_id)

if __name__ == '__main__':

    start = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))

    while True:
        print("%s 开始刷新页面" % datetime.datetime.now())
        item = loop.run_until_complete(tools.get_tuijian_goods())
        datas = item['data']
        ids = []
        for data in datas:
            content = data['content']
            if "haohuo" in content:
                content = json.loads(content)
                url = None
                if 'article_url' in content and "https://haohuo" in content['article_url']:
                    url = content['article_url']
                elif 'raw_ad_data' in content:
                    url = content['raw_ad_data']['web_url']
                else:
                    print(content)
                    continue
                goods_id = url[url.find('?id=')+4:url.find('&')]
                item = loop.run_until_complete(tools.get_num_goods_by_id(goods_id))
                if not item or not item.get('data'):
                    continue
                if not item.get('data').get('name') or item.get('data').get('name') == '':
                    print("下架： %s" % goods_id)
                    continue
                item = item.get('data')
                loop.run_until_complete(check_shop(item.get('shop_id')))

        time.sleep(5)

