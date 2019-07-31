import aiohttp
import asyncio
import requests
import json
import tools

headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            'Accept-Encoding': 'gzip,deflate',
            'Accept- Language': 'zh-CN,en-US,q=0.9',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; MI CC 9 Build/PKQ1.181121.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044807 Mobile Safari/537.36 MMWEBID/4072 MicroMessenger/7.0.5.1440(0x27000537) Process/tools NetType/WIFI Language/zh_CN',
            'Connection': 'keep-alive',
            'Content-Length': '31',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://tp.levote.top",
            "Host": "tp.levote.top",
           'Referer':'Referer: http://tp.levote.top/app/index.php?i=2&c=entry&id=2819&rid=99&isopenlink=first&do=view&m=tyzm_diamondvote&from=timeline',
            'Cookie': 'PHPSESSID=cc8febb367efaad19be7d280332ea6d4; Hm_lvt_08c6f5e17c0761a968c5658ccf6ff5ad=1564228896; Hm_lpvt_08c6f5e17c0761a968c5658ccf6ff5ad=1564244863'
    }


#3354685615617754865

async def get_message(url,data):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers,data=data) as resp:
                if resp.status == 200:
                    return resp
        except Exception as e:
            print("请求异常：%s" % (str(e)))
            pass

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # url = "http://tp.levote.top/app/index.php"
    url = "http://tp.levote.top/app/index.php"
    data = {"i":2,"c":"entry","rid":99,"id":2819,"do":"vote","m":"tyzm_diamondvote","latitude":0,"longitude":0,"verify":0}
    # item = loop.run_until_complete(get_message(url,data))
    # print(item)
    res = requests.post(url,data=json.dumps(data),headers=headers)
    print(res.text)