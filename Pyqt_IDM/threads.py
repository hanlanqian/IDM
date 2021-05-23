import threading
import time
import requests
import globals_varible as g
from PyQt5.QtCore import QThread


class Download_Thread(threading.Thread):
    def __init__(self, url, thread_id, start_bytes, end_bytes):
        super(Download_Thread, self).__init__()
        self.url = url
        self.thread_id = str(thread_id)
        self.start_bytes = start_bytes
        self.end_bytes = end_bytes
        self.result = None

    def run(self):
        headers = g.headers.copy()
        headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        print('线程{}开始解析'.format(self.thread_id))
        r = requests.get(self.url, g.headers)
        data = r.content
        print('线程{}开始写入'.format(self.thread_id))
        with open('test'+self.thread_id+'.tmp', 'wb') as f:
            pass
        with open('test'+self.thread_id+'.tmp', 'ab+') as f:
            f.write(data)


class Download_Thread_Qt(QThread):
    def __init__(self, url, thread_id, start_bytes, end_bytes):
        super(Download_Thread, self).__init__()
        self.url = url
        self.thread_id = str(thread_id)
        self.start_bytes = start_bytes
        self.end_bit = end_bytes
        self.result = None

    def run(self):
        g.headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        r = requests.get(self.url, g.headers)
        data = r.content
        print('线程{}开始下载'.format(self.thread_id))
        with open('test'+self.thread_id+'.tmp', 'wb') as f:
            pass
        with open('test'+self.thread_id+'.tmp', 'ab+') as f:
            f.write(data)


if __name__ == '__main__':
    threads = []
    threads_num = 4
    url = 'https://67ecedb6b9ec5e7a581d5a1c8c8aa0b3.dlied1.cdntips.net/dlied1.qq.com/qqweb/PCQQ/PCQQ_EXE/PCQQ2021.exe' \
          '?mkey=6097eed8716ca3c5&f=0000&cip=113.108.133.48&proto=https&access_type=$header_ApolloNet '
    head_info = requests.head(url, headers=g.headers)
    file_size = int(head_info.headers['Content-Length'])
    g.sub_file_size = g.fileDivision(file_size, threads_num)
    for i in range(threads_num):
        thread = Download_Thread(url, i, g.sub_file_size[i], g.sub_file_size[i + 1])
        threads.append(thread)
    for i in range(threads_num):
        threads[i].start()
    print(g.headers)