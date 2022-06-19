import json
import asyncio
from proxybroker import Broker

with open('config.json') as config_file:
    config_data = json.load(config_file)
proxy_list = []

async def add_list(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        proxy_list.append([proxy.geo.code, proxy.host, proxy.port, proxy.avg_resp_time])

def find_proxies():
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'],
                                       limit=int(config_data["proxies"]["count"])), add_list(proxies))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    return proxy_list
