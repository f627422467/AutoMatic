import sys
sys.path.append("F:\\PyCharmProjects\\AutoMatic")
sys.path.append("E:\\AutoMatic\\")
import tools
from ORM import orm
from Models.Shop import Shop
from Models.Goods import Goods,Goods_Item
from Models.Categorys import Categorys,Category_Cid
import asyncio
from config import configs
import functools
import sys
import datetime

async def parse_page(category_id_object,category_cids):
    item = tools.get_category_all()
    for category_cid in category_cids:
        await Category_Cid.remove(category_cid)
    categorys = item.get('data')
    for fist_level in categorys:
        fist_category = fist_level.get('category')
        fist_category_id = fist_category.get("id")
        fist_category_image = fist_category.get("image")
        fist_category_name = fist_category.get("name")
        fist_category_priority = fist_category.get("priority")
        if category_id_object.keys().__contains__(int(fist_category_id)):
            #修改
            category = category_id_object.get(int(fist_category_id))
            category.id = fist_category_id
            category.parent_id = "0"
            category.name = fist_category_name
            category.priority = fist_category_priority
            category.image = fist_category_image
            await category.update()
        else:
            category = Categorys()
            category.id = fist_category_id
            category.parent_id = "0"
            category.name = fist_category_name
            category.priority = fist_category_priority
            category.image = fist_category_image
            await category.save()

        second_categorys = fist_level.get('sub_category')
        for second_category in second_categorys:
            second_category_id = second_category.get("id")
            second_category_image = second_category.get("image")
            second_category_name = second_category.get("name")
            second_category_priority = second_category.get("priority")
            second_category_parent_id = second_category.get("parent_id")
            second_category_content = second_category.get("content")
            if category_id_object.keys().__contains__(int(second_category_id)):
                #修改
                category = category_id_object.get(int(second_category_id))
                category.id = second_category_id
                category.parent_id = second_category_parent_id
                category.name = second_category_name
                category.priority = second_category_priority
                category.image = second_category_image
                await category.update()
            else:
                category = Categorys()
                category.id = second_category_id
                category.parent_id = second_category_parent_id
                category.name = second_category_name
                category.priority = second_category_priority
                category.image = second_category_image
                await category.save()

            if second_category_content is not None or second_category_content != '':
                contents = second_category_content.split(',')
                for content in contents:
                    category_cid = Category_Cid()
                    category_cid.cid = content
                    category_cid.category_id = second_category_id
                    await category_cid.save()


async def exec():
    print(u"开始抓取分类:%s" % (datetime.datetime.now()))
    categorys = await Categorys.findAll()
    category_id_object = tools.list_to_dict(categorys, 'id')
    category_cids = await Category_Cid.findAll()
    try:
        await parse_page(category_id_object,category_cids)
    except Exception as e:
        print(u"抓取分类%s出错，原因：%s " % (e))
    print(u"抓取分类完成:%s" % (datetime.datetime.now()))


async def init(loop):
    await orm.create_pool(loop=loop, **configs.db)
    await exec()


def done_callback(loop, futu):
    if loop is not None:
        loop.stop()


#更新分类
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    futus = asyncio.gather(init(loop))
    futus.add_done_callback(functools.partial(done_callback, loop))
    loop.run_forever()

