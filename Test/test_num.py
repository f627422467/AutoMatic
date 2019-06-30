import aiohttp
import asyncio
import tools
url = "https://xd.snssdk.com/product/ajaxstaticitem?b_type_new=3&id=3298464650244531351&device_id=57954229867 HTTP/1.1"
headers = {'User-Agent': ' Mozilla/5.0 (Linux; Android 9; MIX 2S Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 NewsArticle/7.3.0 ToutiaoMicroApp/1.22.0.0 PluginVersion/73005',
           'Accept-Encoding': 'gzip',
           # 'Accept- Language': 'en - US, en;q = 0.5',
           "Connection": "keep-alive",
           #'Cookie':'install_id=77029700866;odin_tt=bf79ca74e216dfc7c399631690ef9bce205a49aeed34b1680ade1925ef92c2100d3d03bfb3511fc594700b8db6c10d69;qh[360]=1;sid_guard=1e4594d906681c45a9869793175f31b8%7C1560924815%7C5184000%7CSun%2C+18-Aug-2019+06%3A13%3A35+GMT;uid_tt=5c37550703d871b7c1481a0ce0003b63;sid_tt=1e4594d906681c45a9869793175f31b8;sessionid=1e4594d906681c45a9869793175f31b8;ttreq=1$932646705ddf9d5d962e36cd1eedfa465a41b731',
           'Referer':'https://tmaservice.developer.toutiao.com?appid=tt7cca0a77e3e0cd15&version=0.0.161',
            'x-xiaodian-device-id': '57954229867',
            'x-xiaodian-install-id': '77029700866',
            'Host': 'xd.snssdk.com'
    }

async def get_message():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    print(await resp.json())
        except Exception as e:
            print("请求异常：%s" % (str(e)))
            pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # item = loop.run_until_complete(get_message())
    item = loop.run_until_complete(tools.get_num_goods_by_id("3352401786169339668"))
    print(item)