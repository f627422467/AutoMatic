from urllib.parse import urlencode
import requests
import aiohttp
import datetime
import utils
import random
import aiomysql
import numpy
import time

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
        'size': 10,
        'b_type_new': 0,
        'type': 5,
        'sort': 1
    }
    url = 'https://haohuo.snssdk.com/productcategory/getShopList?' + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers[
        'Referer'] = 'https://haohuo.jinritemai.com/views/shop/index?id=%s&origin_type=0&origin_id=0&new_source_type=47&new_source_id=0&source_type=47&source_id=0&come_from=0' % shop_id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


async def get_goods_by_shop_sort(shop_id, page, type, sort):
    params = {
        'shop_id': shop_id,
        'page': page,
        'size': 10,
        'b_type_new': 0,
        'type': type,
        'sort': sort
    }
    url = 'https://haohuo.snssdk.com/productcategory/getShopList?' + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers[
        'Referer'] = 'https://haohuo.jinritemai.com/views/shop/index?id=%s&origin_type=0&origin_id=0&new_source_type=47&new_source_id=0&source_type=47&source_id=0&come_from=0' % shop_id
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

async def get_num_goods_by_id(goods_id):
    params = {
        'id': goods_id,
        'b_type_new': 3
    }
    url = "https://xd.snssdk.com/product/ajaxstaticitem?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Host'] = 'xd.snssdk.com'
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)

async def get_tuijian_goods():
    url = "https://is-hl.snssdk.com/api/news/feed/v88/?list_count=10&support_rn=4&refer=1&refresh_reason=1&session_refresh_idx=18&count=20&min_behot_time="+str(int(time.time()))+"&last_refresh_sub_entrance_interval="+str(int(time.time()))+"&gps_mode=7&loc_mode=1&loc_time="+str(int(time.time()))+"&latitude=32.15122444816348&longitude=118.73658058848514&city=%E5%8D%97%E4%BA%AC%E5%B8%82&tt_from=pull&plugin_enable=3&client_extra_params=%7B%22playparam%22%3A%22codec_type%3A1%22%7D&st_time=1838&sati_extra_params=%7B%22last_click_item_list%22%3A%5B%5D%7D&iid=77502709030&device_id=57954229867&ac=wifi&channel=xiaomi&aid=13&app_name=news_article&version_code=731&version_name=7.3.1&device_platform=android&ab_version=668774%2C765191%2C976875%2C821968%2C857804%2C952276%2C757284%2C991602%2C983226%2C679101%2C660830%2C830855%2C947963%2C942634%2C662176%2C955526%2C665173%2C674055%2C643892%2C671752%2C654104%2C649426%2C677128%2C710077%2C801968%2C707372%2C661900%2C668775%2C982555%2C971379%2C739394%2C662099%2C759652%2C661781&ab_feature=94563%2C102749&ssmix=a&device_type=MIX+2S&device_brand=Xiaomi&language=zh&os_api=28&os_version=9&openudid=65eabf5f997f8c77&manifest_version_code=731&resolution=1080*2030&dpi=440&update_version_code=73109&_rticket=1562161437652&plugin=18766&pos=5r_-9Onkv6e_eBAKeScxeCUfv7G_8fLz-vTp6Pn4v6esrKWzqq6rqKWtqKWlqaWorKmxv_H86fTp6Pn4v6eur7OsqKyvr6mpqaWsq66ppbG__PD87d706eS_p794EAp5JzF4JR-_sb_88Pzt0fLz-vTp6Pn4v6esrKWzqq6trKyusb_88Pzt0fzp9Ono-fi_p66vs6ypqKippOA%3D&fp=F2TrPzQ5L2HSFlTrL2U1F2ZuLSTZ&tma_jssdk_version=1.23.0.6&rom_version=miui__v10.2.2.0.pdgcnxm&ts=1562161437&as=abc27fec685d1cb11dc27f&mas=0119932353f99959d373f979b98507b28759d373f919b3b379f9b3&cp=55d51fc5b311dq1 HTTP/1.1"
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Host'] = 'is-hl.snssdk.com'
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


def reutrn_value(field):
    if type(field) is bytes:
        field = ord(field)
        return '%d' % field
    elif type(field) is bool:
        return '%d' % (numpy.array(field) + 0)
    elif type(field) is str:
        return '\'%s\'' % aiomysql.escape_string(field)
    else:
        return '\'%s\'' % field


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
        'app_id': 'undefined',
        'area_type': 5,
        'area_id': 0,
        'origin_type': 303,
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
async def get_activity_goods(id, page):
    params = {
        'id': id,
        'page': page,
        'size': 10,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/channel/ajaxActivityGoods?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers[
        'Referer'] = 'https://haohuo.jinritemai.com/views/channel/flash?a=1&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0'
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 值点精选，查询分类
async def get_detail_by_mertial_id(id):
    params = {
        'id': id,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/channel/material?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.snssdk.com'
    headers[
        'Referer'] = 'https://haohuo.snssdk.com/views/channel/material?id=%s&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0' % id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 值点精选，根据分类查询商品
async def get_goods_by_detail_id(material_id, id, page):
    params = {
        'material_id': material_id,
        'id': id,
        'page': page,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/channel/materialDetail?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.snssdk.com'
    headers[
        'Referer'] = 'https://haohuo.snssdk.com/views/channel/material?id=%s&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0' % id
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 秒杀（秒杀场次）
async def get_kills():
    params = {
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/seckill/seckillMultiSessionList?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers[
        'Referer'] = 'https://haohuo.jinritemai.com/views/channel/seckill?a=1&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0'
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


# 根据秒杀场次，获取商品
async def get_goods_by_campaign_id(campaign_id, page):
    params = {
        'campaign_id': campaign_id,
        'req_id': 1,
        'page': page,
        'pageSize': 10,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/seckill/seckillCampaignGoodsList?" + urlencode(params)
    headers = utils.get_defind_headers()
    headers['User-Agent'] = utils.random_agent()
    headers['Origin'] = 'https://haohuo.jinritemai.com'
    headers[
        'Referer'] = 'https://haohuo.jinritemai.com/views/channel/seckill?a=1&origin_type=3030005&origin_id=0&new_source_type=5&new_source_id=1&source_type=5&source_id=1&come_from=0'
    proxy = utils.get_proxies()
    return await utils.aiohttp_get(url, headers, proxy)


def get_goods(goods_id):
    params = {
        'id': goods_id,
        'b_type_new': 0
    }
    url = "https://haohuo.snssdk.com/product/fxgajaxstaticitem?" + urlencode(params)
    header2s = {
        'user-agent': phton_user_agent,
        'Referer': 'https://haohuo.snssdk.com/views/product/item2?id=%s' % goods_id,
    }
    try:
        response = requests.get(url, headers=header2s)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("请求异常：%s" % e)
        pass


def get_sell_num(sell_num):
    if type(sell_num) == int:
        return sell_num
    if sell_num.__contains__("万+"):
        return int(round(float(sell_num.strip('万+')) * 10000, 0))
    elif sell_num.__contains__("+"):
        return int(sell_num.strip('+'))
    elif sell_num.__contains__("万"):
        return int(round(float(sell_num.strip('万')) * 10000, 0))
    else:
        return int(sell_num)


if __name__ == '__main__':
    sell_num = get_sell_num(100)
    print(sell_num)
