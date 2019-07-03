import aiohttp
import asyncio
import tools
import datetime
import time
import json



headers = {'User-Agent': ' Mozilla/5.0 (Linux; Android 9; MIX 2S Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 NewsArticle/7.3.0 ToutiaoMicroApp/1.22.0.0 PluginVersion/73005',
           'Accept-Encoding': 'gzip',
           "Connection": "keep-alive",
            # 'sdk-version': '1',
            # 'X-Gorgon': '03006cc00000e6ce226da76ab9853eca89ad66bad41d08946de4',
            # 'X-Khronos': '1562159119',
            # 'X-SS-REQ-TICKET': '1562159119024',
            # 'X-Tt-Token': '005f8cdcaaf4f4de5210692192388e4b3a8d64132653f386aca5d51988ffafcacd712fee22da8c97187e704677d6b12e694d',
            'Host': 'is-hl.snssdk.com'
    }

async def get_message():
    async with aiohttp.ClientSession() as session:
        url = "https://is-hl.snssdk.com/api/news/feed/v88/?list_count=10&support_rn=4&refer=1&refresh_reason=1&session_refresh_idx=18&count=20&min_behot_time="+str(int(time.time()))+"&last_refresh_sub_entrance_interval="+str(int(time.time()))+"&gps_mode=7&loc_mode=1&loc_time="+str(int(time.time()))+"&latitude=32.15122444816348&longitude=118.73658058848514&city=%E5%8D%97%E4%BA%AC%E5%B8%82&tt_from=pull&plugin_enable=3&client_extra_params=%7B%22playparam%22%3A%22codec_type%3A1%22%7D&st_time=1838&sati_extra_params=%7B%22last_click_item_list%22%3A%5B%5D%7D&iid=77502709030&device_id=57954229867&ac=wifi&channel=xiaomi&aid=13&app_name=news_article&version_code=731&version_name=7.3.1&device_platform=android&ab_version=668774%2C765191%2C976875%2C821968%2C857804%2C952276%2C757284%2C991602%2C983226%2C679101%2C660830%2C830855%2C947963%2C942634%2C662176%2C955526%2C665173%2C674055%2C643892%2C671752%2C654104%2C649426%2C677128%2C710077%2C801968%2C707372%2C661900%2C668775%2C982555%2C971379%2C739394%2C662099%2C759652%2C661781&ab_feature=94563%2C102749&ssmix=a&device_type=MIX+2S&device_brand=Xiaomi&language=zh&os_api=28&os_version=9&openudid=65eabf5f997f8c77&manifest_version_code=731&resolution=1080*2030&dpi=440&update_version_code=73109&_rticket=1562161437652&plugin=18766&pos=5r_-9Onkv6e_eBAKeScxeCUfv7G_8fLz-vTp6Pn4v6esrKWzqq6rqKWtqKWlqaWorKmxv_H86fTp6Pn4v6eur7OsqKyvr6mpqaWsq66ppbG__PD87d706eS_p794EAp5JzF4JR-_sb_88Pzt0fLz-vTp6Pn4v6esrKWzqq6trKyusb_88Pzt0fzp9Ono-fi_p66vs6ypqKippOA%3D&fp=F2TrPzQ5L2HSFlTrL2U1F2ZuLSTZ&tma_jssdk_version=1.23.0.6&rom_version=miui__v10.2.2.0.pdgcnxm&ts=1562161437&as=abc27fec685d1cb11dc27f&mas=0119932353f99959d373f979b98507b28759d373f919b3b379f9b3&cp=55d51fc5b311dq1 HTTP/1.1"
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print("请求异常：%s" % (str(e)))
            pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    item = loop.run_until_complete(get_message())
    datas = item['data']
    for data in datas:
        content = data['content']
        if "haohuo" in content:
            content = json.loads(content)
            url = None
            if 'article_url' in content and "https://haohuo" in content['article_url']:
                url = content['article_url']
            else:
                url = content['raw_ad_data']['web_url']
            id = url[url.find('?id=') + 4:url.find('&')]
            print(id)
            print(url)
            print(content)