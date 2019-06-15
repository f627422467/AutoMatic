import asyncio
import time


async def sellp():
    await asyncio.sleep(3)

async def wget():
    for i in range(10):
        print("执行 %s" % i)
        await sellp()
        print("执行 %s 完毕" % i)


task = []
loop = asyncio.get_event_loop()
task.append(asyncio.ensure_future(wget()))
task.append(asyncio.ensure_future(wget()))
loop.run_until_complete(asyncio.wait(task))
loop.close()