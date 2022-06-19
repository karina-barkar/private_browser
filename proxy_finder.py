import json, requests, asyncio
from proxybroker import Broker

with open('config.json') as config_file:            # читаем конфиг
    config_data = json.load(config_file)            # из которого потом получим сколько нужно различных прокси
proxy_list = []


async def add_list(proxies):
    """ асинхронная функция получения прокси и добавления в список """
    global proxy_list
    while True:
        proxy = await proxies.get()                 # ждём прокси
        if proxy is None:                           # и добавляем в список, если он не пустой
            break
        proxy_list.append([proxy.geo.code, proxy.host, proxy.port, proxy.avg_resp_time])


def find_proxies():
    """ функция поиска списка рабочих прокси-серверов
     Поскольку данная библиотека работает крайне нестабильно, список прокси был предустановлен.
     Если у вас она работает, то можно в конфиге config.json установить значение "use_proxybroker" равным 1 """
    global proxy_list
    if config_data["proxies"]["use_proxybroker"]:
        proxies = asyncio.Queue()
        broker = Broker(proxies)                        # брокер поиска из библиотеки proxybroker
        tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], # будем искать http и https прокси
                                           limit=int(config_data["proxies"]["count"])), add_list(proxies))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)                  # запуск цикла поиска прокси-серверов
    else:
        try:
            responce = requests.get(config_data["proxies"]["proxies_url"])
            proxy_list = json.loads(responce.content)
        except:
            pass

    if len(proxy_list) == 0:                        # костыль, на случай если не удалось найти ни одного прокси
        proxy_list = [['US', '35.170.197.3', 8888, 0.19], ['US', '168.8.172.2', 80, 0.15],
                      ['US', '143.198.242.86', 8048, 0.17], ['US', '34.145.226.144', 8080, 0.17],
                      ['US', '104.200.18.76', 3128, 0.22], ['DE', '95.217.72.247', 3128, 0.26],
                      ['--', '45.167.124.5', 9992, 0.36], ['EC', '157.100.12.138', 999, 0.39],
                      ['CN', '120.26.14.114', 8888, 0.55], ['KR', '183.111.25.253', 8080, 0.65],
                      ['EC', '186.5.5.125', 8080, 0.86], ['RU', '178.66.182.76', 3128, 1.02],
                      ['--', '194.169.167.199', 8080, 1.35], ['IN', '117.241.129.137', 9812, 2.03],
                      ['CO', '181.225.68.27', 999, 2.21], ['US', '47.89.185.178', 8888, 2.25],
                      ['US', '107.172.73.179', 7890, 2.36], ['UZ', '195.211.180.156', 3128, 1.56],
                      ['BO', '200.105.215.18', 33630, 1.14], ['PE', '181.176.211.168', 8080, 0.33]]
    return proxy_list
