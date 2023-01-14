import json
import requests

with open("config.json") as config_file:  # читаем конфиг
    config_data = json.load(
        config_file
    )  # из которого потом получим сколько нужно различных прокси
proxy_list = []


def find_proxies():
    global proxy_list
    try:
        responce = requests.get(config_data["proxies"]["proxies_url"])
        proxies_list = json.loads(responce.content)
        for proxy_counter in range(int((config_data["proxies"]["count"]))):
            proxy_list.append(
                [
                    f"{proxies_list[proxy_counter]['geolocation']['country']},"
                    f" {proxies_list[proxy_counter]['geolocation']['city']}",
                    proxies_list[proxy_counter]["ip"],
                    proxies_list[proxy_counter]["port"],
                    proxies_list[proxy_counter]["geolocation"]["countryCode"],
                ]
            )
    except:
        pass

    if (
        len(proxy_list) == 0
    ):  # костыль, на случай если не удалось найти ни одного прокси
        proxy_list = [
            ["United States, North Bergen", "161.35.48.185", 443, "US"],
            ["United States, Oak Lawn", "209.37.250.19", 80, "US"],
            ["United States, Kansas City", "190.92.190.121", 3128, "US"],
            ["United States, Kansas City", "190.92.190.121", 3128, "US"],
            ["United States, Los Angeles", "23.225.72.125", 3503, "US"],
            ["Germany, Falkenstein", "148.251.150.106", 3128, "DE"],
            ["France, Paris", "51.158.154.173", 3128, "FR"],
            ["Ecuador, Puebloviejo", "45.70.236.194", 999, "EC"],
            ["United States, Los Angeles", "23.225.72.123", 3501, "US"],
            ["Japan, Yokohama", "49.212.143.246", 6666, "JP"],
            ["United States, Los Angeles", "104.223.135.178", 10000, "US"],
            ["Singapore, Singapore", "188.166.241.174", 443, "SG"],
            ["Palestine, Nablus", "212.14.243.29", 8080, "PS"],
            ["United States, North Bergen", "161.35.48.185", 443, "US"],
            ["Iran, Tehran", "213.233.182.39", 8000, "IR"],
            ["France, Strasbourg", "51.254.32.245", 3128, "FR"],
            ["United States, Los Angeles", "23.225.72.124", 3502, "US"],
            ["Indonesia, Bantarwaru", "103.173.139.252", 8080, "ID"],
            ["United States, Los Angeles", "23.225.72.122", 3500, "US"],
            ["United States, Los Angeles", "23.225.72.124", 3502, "US"],
            ["Indonesia, Banjar Pemangkalan", "43.243.184.24", 8080, "ID"],
            ["Singapore, Singapore", "47.241.165.133", 443, "SG"],
            ["Indonesia, Bandung", "103.167.68.76", 8080, "ID"],
            ["Hong Kong, Hong Kong", "119.8.27.129", 3128, "HK"],
            ["Indonesia, Rejomulyo", "103.106.112.18", 1234, "ID"],
            ["United States, St Louis", "154.38.161.241", 80, "US"],
            ["United States, Ashburn", "129.153.146.63", 5566, "US"],
            ["Indonesia, Jakarta", "36.66.171.243", 8080, "ID"],
            ["Honduras, Nueva Ocotepeque", "179.49.113.230", 999, "HN"],
            ["United States, North Bergen", "143.198.182.218", 80, "US"],
            ["Argentina, Jose Maria Ezeiza", "200.106.187.242", 999, "AR"],
            ["Russia, Moscow", "185.15.172.212", 3128, "RU"],
            ["Germany, Falkenstein", "5.9.152.185", 80, "DE"],
            ["Nigeria, Kaduna", "105.112.130.186", 8080, "NG"],
            ["United States, Clifton", "104.131.19.48", 3128, "US"],
            ["Pakistan, Islamabad", "116.71.136.98", 8080, "PK"],
            ["Colombia, Ibague", "190.109.16.145", 999, "CO"],
            ["France, Marseille", "144.24.207.98", 8080, "FR"],
            ["Indonesia, Jakarta", "36.95.17.93", 9812, "ID"],
            ["Kyrgyzstan, Bishkek", "212.112.127.20", 8080, "KG"],
            ["United States, Frankton", "149.57.11.129", 8181, "US"],
            ["Libya, Tripoli", "102.68.128.217", 8080, "LY"],
            ["Russia, Samara", "88.200.132.154", 8080, "RU"],
            ["Puerto Rico, Martorell", "154.64.211.145", 999, "PR"],
            ["France, Strasbourg", "51.254.32.245", 3128, "FR"],
            ["United States, Kearney", "24.51.32.59", 8080, "US"],
            ["Iran, Tehran", "217.146.217.178", 3128, "IR"],
            ["United States, Charlottesville", "47.89.185.178", 8888, "US"],
            ["United States, West Gulfport", "160.3.168.70", 8080, "US"],
            ["Russia, Moscow", "185.15.172.212", 3128, "RU"],
        ]

    return proxy_list
