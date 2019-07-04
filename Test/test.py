from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from ByTuiJian import tuijian_exec
import asyncio
from ORM import orm
from config import configs
import time

def tick(loop):
    tuijian_exec.exec(loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop=loop, **configs.db))
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=3,args=[loop],)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C    '))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

