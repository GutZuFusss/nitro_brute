import math
import os
import os.path
import io
import requests
from threading import Thread
import sys
import time

num_threads = 8
initial_proxies = 450

timeout = 2
good_list = []


def verify_list(proxy_list, thread_number):
    global good_list, timeout
    print('[Thread: ' + str(thread_number) + '] Now checking fetched proxies\n')
    working_list = []
    for prox in proxy_list:
        try:

            proxy_dict = {
                "https": "https://"+prox+"/",
            }

            r = requests.get("http://ipinfo.io/json", proxies=proxy_dict, timeout=timeout)
            site_code = r.json()
            ip = site_code['ip']
            print('[Thread: ' + str(thread_number) + '] Current IP: ' + ip + '\n')
            print('[Thread: ' + str(thread_number) + '] Proxy works: ' + prox + '\n')
            working_list.append(prox)
        except Exception as e:
            print('[Thread: ' + str(thread_number) + '] Proxy failed: ' + prox + '\n')
            print('[Thread: ' + str(thread_number) + '] Proxy failed message: ' + e + '\n')
    print('[Thread: ' + str(thread_number) +  '] Working Proxies: ' + str(len(working_list)) + '\n')
    good_list += working_list


def get_proxies():
    proxy_list = []
    print('[All         ] Started fetching initial proxies.\n')
    for x in range(0, int(initial_proxies/5)): # very good service, only 5 at a time without payment tho -> loop
        fetched = requests.get("http://pubproxy.com/api/proxy?limit=5&format=txt&type=https&country=de,nl,fr,be,at,ch,lu,it,pl,cz,dk,es", timeout=timeout).text
        for line in io.StringIO(fetched):
            proxy_list.append(line.strip())
        print('[All         ] ' + str(x*5) + ' / ' + str(initial_proxies))
        time.sleep(0.5)

    # check for duplicates & return
    proxy_list_nd = list(set(proxy_list))
    print('[All         ] Dublicates removed: ' + str(len(proxy_list)-len(proxy_list_nd)) + '\n')
    return proxy_list_nd


def setup(number_threads):
    thread_amount = float(number_threads)
    proxy_list = get_proxies()
    amount = int(math.ceil(len(proxy_list)/thread_amount))
    proxy_lists = [proxy_list[x:x+amount] for x in range(0, len(proxy_list), amount)]
    if len(proxy_list) % thread_amount > 0.0:
        proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
    return proxy_lists


def start(threads):
    start_time = time.time()
    lists = setup(threads)
    thread_list = []
    count = 0
    for l in lists:
        thread_list.append(Thread(target=verify_list, args=(l, count)))
        thread_list[len(thread_list)-1].start()
        count += 1

    for x in thread_list:
        x.join()

    f = open('proxies/fetched_proxies_' + str(start_time) + '.txt', 'w+')
    to_write = ''
    for i in good_list:
        to_write += i+'\n'
    f.write(to_write)
    f.close()
    stop_time = time.time()
    print('[{0:.2f} seconds]\n'.format(stop_time-start_time))
    print('[Finished    ] Met requirements / Initial: ' + str(len(good_list)) + ' / ' + str(initial_proxies) + '\n')


if __name__ == "__main__":
    start(num_threads)
