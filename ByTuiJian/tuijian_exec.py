import sys

sys.path.append("/opt/AutoMatic/")
sys.path.append("D:\\AutoMatic\\")
from ByTmp import tmp_producer
import consumer
import threading
import queue
import asyncio
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods, Goods_Ad
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
        shop = Shop(shop_id=shop_id, shop_url=shop_url,create_time=datetime.datetime.now())
        await shop.save()
    else:
        print("%s已存在" % shop_id)


# if __name__ == '__main__':
def exec(loop):
    start = datetime.datetime.now()
    # loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    try:
        print("%s 开始刷新页面" % datetime.datetime.now())
        item = loop.run_until_complete(tools.get_tuijian_goods())
        datas = item['data']
        ids = []
        for data in datas:
            content = data['content']
            shop_id = None
            goods_id = None
            if "haohuo" in content:
                content = json.loads(content)
                url = None
                if 'article_url' in content and "https://haohuo" in content['article_url']:
                    url = content['article_url']
                elif 'raw_ad_data' in content:
                    url = content['raw_ad_data']['web_url']
                elif 'commoditys' in content:
                    commoditys = content['commoditys']
                    for commodity in commoditys:
                        if 'charge_url' in commodity:
                            url = commodity['charge_url']
                            break
                elif 'data' in content:
                    data2s = content['data']
                    for data2 in data2s:
                        if 'raw_data' in data2:
                            raw_data = data2['raw_data']
                            if 'deversion' in raw_data and raw_data['deversion']:
                                deversion = raw_data['deversion']
                                url = deversion['schema_url']
                                if 'shop%2Findex%3Fid%3D' in url:
                                    shop_id = url[url.find('id%3D')+5:url.find('%26')]
                                elif 'product%2Fitem2%3Fid%3D' in url:
                                    goods_id = url[url.find('id%3D')+5:url.find('%26')]
                                break
                elif "content" in content and "https://haohuo" in content['content']:
                    url = content['content']
                elif "log_pb" in content:
                    log_pb = content['log_pb']
                    if 'url_list' in log_pb:
                        url_list = json.loads(log_pb['url_list'])
                        for uri in url_list:
                            if "https://haohuo" in uri:
                                url = uri
                else:
                    print(content)
                    continue
                if not shop_id:
                    if not goods_id :
                        if "id%3D" in url:
                            goods_id = url[url.find('id%3D') + 5:url.find('%26')]
                        else:
                            goods_id = url[url.find('?id=') + 4:url.find('&')]
                        print(goods_id)
                    item = loop.run_until_complete(tools.get_num_goods_by_id(goods_id))
                    if not item or not item.get('data'):
                        continue
                    if not item.get('data').get('name') or item.get('data').get('name') == '':
                        print("下架： %s" % goods_id)
                        continue
                    item = item.get('data')
                    goods_ad = loop.run_until_complete(Goods_Ad.find_one('goods_id=?', goods_id))
                    if goods_ad:
                        goods_ad.num = goods_ad.num + 1
                        loop.run_until_complete(Goods_Ad.update(goods_ad))
                    else:
                        goods_ad = Goods_Ad()
                        goods_ad.goods_id = goods_id
                        goods_ad.num = 1
                        loop.run_until_complete(Goods_Ad.save(goods_ad))
                    shop_id = item.get('shop_id')
                loop.run_until_complete(check_shop(shop_id))
    except Exception as e:
        print(str(e))

