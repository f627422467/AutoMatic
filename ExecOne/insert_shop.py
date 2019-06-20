import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
import tools
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods, Goods_Item, Goods_Tmp
import asyncio
from config import configs
import functools
import sys
import datetime


async def check_shop(shop_id):
    shop_url = 'https://haohuo.snssdk.com/views/shop/index?id=' + shop_id
    shop = await Shop.findAll('shop_id=?', [shop_id])
    print(shop)
    if len(shop) == 0:
        print("不存在")
        shop = Shop(shop_id=shop_id, shop_url=shop_url)
        shop.id = await shop.save()
        return shop
    return shop[0]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))

    with open(r'F:\PyCharmProjects\AutoMatic\shop_ids.txt', 'r', encoding='utf-8') as f:
        shop_ids = f.readlines()
        for shop_id in shop_ids:
            shop_id = shop_id.strip('\n')
            loop.run_until_complete(check_shop(shop_id))
