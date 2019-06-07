from urllib.parse import urlencode
import requests
import aiohttp
import datetime
import utils
import random

pc_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'

phton_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

proxyHost = "58.218.201.122"
proxyPort = "2436"

proxyMeta = "http://%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}

proxy = "http://58.218.200.248:7861"


# 通过店铺获取全部商品
async def get_goods_by_shop(shop_id, page):
    params = {
        'shop_id': shop_id,
        'page': page,
        'pageSize': 20,
        'b_type_new': 0,
        'type': 5,
        'sort': 1
    }
    url = 'https://haohuo.snssdk.com/productcategory/getShopList?' + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers['Referer'] = 'https://haohuo.jinritemai.com/views/shop/index?id=%s' % shop_id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 通过店铺获取首页商品
async def get_first_goods_by_shop(shop_id, page):
    params = {
        'shop_id': shop_id,
        'page': page,
        'pageSize': 20,
        'b_type_new': 0,
    }
    url = 'https://haohuo.snssdk.com/shop/goodsList?' + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers['Referer'] = 'https://haohuo.jinritemai.com/views/shop/index?id=%s' % shop_id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 通过分类获取商品
async def get_goods_by_category(cids, id, parentid, page):
    params = {
        'second_cid': cids,
        'type': 5,
        'sort': 1,  # 销量排序
        'page': page,
        'pageSize': 10
    }
    url = "https://haohuo.snssdk.com/productcategory/getList?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers[
        'Referer'] = 'https://haohuo.jinritemai.com/views/channel/categorychoose?cids=%s&parent_id=%s&id=%s&fresh_come=undefined&origin_type=3030005&origin_id=0&new_source_type=100&new_source_id=0&source_type=100&source_id=0&come_from=0' % (
        cids, parentid, id)
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 通过商品ID更新商品(User-Agent，必须使用手机的，否则抓不到数据)
async def get_goods_by_id(goods_id):
    params = {
        'id': goods_id,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/product/fxgajaxstaticitem?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers['Referer'] = 'https://haohuo.jinritemai.com/views/product/item2?id=%s' % goods_id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 获取所有分类信息
def get_category_all():
    params = {
        'version': 1,
        'is_category': 1
    }
    url = "https://haohuo.snssdk.com/channel/ajaxCategoryAll?" + urlencode(params)
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        'Origin': 'https://haohuo.jinritemai.com',
        'Referer': 'https://haohuo.jinritemai.com/views/channel/categories?a=1&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("请求异常：%s" % e)
        pass


def list_to_dict(lists, key):
    dit = {}
    for element in lists:
        if key not in element.__fields__ and key is not element.__primary_key__:
            raise Exception("Key %s 不存在！" % key)
        dit[element[key]] = element
    return dit


def get_temp_table():
    time_now = datetime.datetime.now().strftime("%Y%m%d")
    return "tmp_%s" % time_now


def get_random_num(num):
    return ''.join(str(random.choice(range(10))) for _ in range(num))


# TODO
# 获取头条榜单
# 活动ID，随机12位。115118308595
async def get_activity_by_id(activity_id, _):
    params = {
        'id': activity_id,
        '_': _,
        'b_type_new': 0
    }
    url = "https://bolt.jinritemai.com/api/activity/detail?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Referer'] = 'https://bolt.jinritemai.com/h5/activity?id=%s' % activity_id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 通过material_id查询
async def get_goods_by_material_id(activity_id, _, material_id, page):
    params = {
        'material_id': material_id,
        'page': page,
        'size': 10,
        '_': _,
        'b_type_new': 0
    }
    url = "https://luban.snssdk.com/bolt/productlist?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://bolt.jinritemai.com'
    headers['Referer'] = 'https://bolt.jinritemai.com/h5/activity?id=%s' % activity_id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)

# 获取推荐精选
async def get_recommend_goods(page):
    params = {
        'cids': '',
        'page': page,
        'size': 10,
        'addActivity': 1,
        'app_id':'undefined',
        'area_type':5,
        'area_id':0,
        'origin_type':303,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/channel/ajaxGetGoods?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers['Referer'] = 'https://haohuo.jinritemai.com/channel/list?origin_type=303'
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)

# 获取好货

# 值点精选

if __name__ == '__main__':
    print(''.join(str(random.choice(range(10))) for _ in range(12)))
