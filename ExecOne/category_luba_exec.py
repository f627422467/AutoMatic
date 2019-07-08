import sys

sys.path.append("D:\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
import tools
from ORM import orm
from Models.Categorys import Luban_Categorys
import asyncio
from config import configs
import functools
import sys
import datetime
import aiohttp
import asyncio


import tools
# url = "https://luban.jinritemai.com/product/tproduct/getGoodsCategory?__token=23233c0d33e4a9649d17658ce6637fc6&_=1562595264191"
headers = {'User-Agent': ' Mozilla/5.0 (Linux; Android 9; MIX 2S Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 NewsArticle/7.3.0 ToutiaoMicroApp/1.22.0.0 PluginVersion/73005',
           'Accept-Encoding': 'gzip',
           # 'Accept- Language': 'en - US, en;q = 0.5',
           "Connection": "keep-alive",
           'Cookie':'eed.js%3Asession=%7B%22id%22%3A%2216bc2b9b74754e-04dd9f608bad46-e343166-1fa400-16bc2b9b74871c%22%2C%22page%22%3A%2216bcf5c825e4f6-0048189e270972-75296032-448e0-16bcf5c825f7ed%22%2C%22created%22%3A1562552074849%2C%22lastPage%22%3A%2216bcf5bdce33c5-02134ae86c3f9a-e343166-15f900-16bcf5bdce450e%22%7D; PHPSESSID=kith7p86qg3eari19uk2jf6vl7; _ga=GA1.2.1506354422.1562594874; _gid=GA1.2.618117090.1562594874; _gat_gtag_UA_101725298_1=1',
           'Referer':'https://luban.jinritemai.com/index.html',
    }

async def get_category(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print("请求异常：%s" % (str(e)))
            pass

def warp_entiry(data,parent_id):
    luban_category = Luban_Categorys()
    luban_category.id = data.get('id')
    if not parent_id:
        luban_category.parent_id = None
    else:
        luban_category.parent_id = parent_id
    luban_category.name = data.get('name')
    luban_category.level = data.get('level')
    return luban_category

async def exec(parent_id):
    if not parent_id:
        url = "https://luban.jinritemai.com/product/tproduct/getGoodsCategory?__token=23233c0d33e4a9649d17658ce6637fc6&_=1562595264191"
    else:
        url = "https://luban.jinritemai.com/product/tproduct/getGoodsCategory?cid=%s&__token=23233c0d33e4a9649d17658ce6637fc6&_=1562595264191" % parent_id
    item = await get_category(url)
    if not item:
        return
    datas = item['data']
    for data in datas:
        luban_category = warp_entiry(data,parent_id)
        await luban_category.save()
        await exec(data.get('id'))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    #清除分类信息
    loop.run_until_complete(Luban_Categorys.del_by())
    #获取分类
    loop.run_until_complete(exec(None))

