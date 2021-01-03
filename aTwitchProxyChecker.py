import requests
import json
import queue
import threading
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from colorama import init, Fore
init()

proxies_q = queue.Queue()

def settings():
    try:
        confs = json.loads(open('./settings.json','r').read())
        print(f"{Fore.CYAN}Settings loaded!")
        return confs
    except:
        print(f"{Fore.RED}settings.json not found!")

def array(arr, q):
    for i in arr:
        q.put(i)
    return q

def save_proxy(proxy, conf):
    print(f"{Fore.WHITE}{proxy} {Fore.GREEN}This proxy is compatible with Twitch!")
    compatible_proxy_list = open(conf['verified_proxy_location'], 'a')
    compatible_proxy_list.write(":".join([proxy])+"\n")
    compatible_proxy_list.close()

def get_header():
    return {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Host': 'www.twitch.tv',
        'Accept': '*/*',
        'Accept-Language': 'en-US',
        'Content-Type': 'text/html',
        'Referer': 'https://www.google.com/',
        'Connection': 'close'
    }

def proxy_check(conf):
    try:
        get_header()
        rs = requests.Session()
        proxy = proxies_q.get()
        proxies_q.task_done()
        if proxy != 'none':
            proxies = {
                'http' : 'http://' + proxy,
                'https' : 'https://' + proxy
            }
            rs.proxies.update(proxies)
    
        rs.post('https://www.twitch.tv', proxies=proxies, timeout=conf['timeout'])
        save_proxy(proxy, conf)
    except:
        print(f"{Fore.WHITE}{proxy} {Fore.RED}This proxy is not compitable with Twitch.")
        return False
    return True

def system(conf):
    while not proxies_q.empty():
        proxy_check(conf)
  
def engine():
    global proxies_q
    conf = settings()
    loaded_proxy_count = sum(1 for line in open(conf['proxy_location']))
    os.system("title aTwitchProxyChecker by abloit")
    print(f"{Fore.CYAN}Twitch proxy checker started!")
    print(f"Loaded Proxy Count: {loaded_proxy_count}")
    data = [x.rstrip() for x in open(conf['proxy_location'], 'r').readlines()]
    proxies = []
    already_done = [x.rstrip() for x in open(conf['verified_proxy_location'], 'r').readlines()]
    for p in data:
        try:
            if p not in already_done:
                proxies.append(p)
        except:
            pass
    proxies_q = array(proxies, proxies_q)
    
    tx = []
    for i in range(conf['range_count']):
        mT = threading.Thread(target=system, args=(conf, ))
        mT.start()
        tx.append(mT)
    for t in tx:
        t.join()
    print(f"{Fore.GREEN}All proxies checked!")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    engine()
