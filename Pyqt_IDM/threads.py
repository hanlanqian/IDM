import threading
import time
import requests
import globals_varible as g




class Download_Thread(threading.Thread):
    def __init__(self, url):
        super(Download_Thread, self).__init__()
        self.url = url
        self.result = None

    def run(self):
        requests.get(self.url, g.headers)

if __name__ == '__main__':
    thread1 = Download_Thread()
    thread2 = Download_Thread()
    thread1.start()
    print(time.time())
    thread2.start()
    # print('1')
    # print(time.time())
    # print('1')
    # print(time.time())