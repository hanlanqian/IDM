from threading import Thread, Lock
import time
import requests
import globals_varible as g
import os
from PyQt5.QtCore import QThread


class Download_Thread(Thread):
    def __init__(self, url, thread_id, start_bytes, end_bytes):
        super(Download_Thread, self).__init__()
        self.url = url
        self.thread_id = str(thread_id)
        self.start_bytes = start_bytes
        self.end_bytes = end_bytes - 1
        self.result = None
        print(self.start_bytes, self.end_bytes)

    def run(self):
        headers = g.headers.copy()
        headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        print('线程{}开始解析'.format(self.thread_id))
        r = requests.get(self.url, headers)
        data = r.content
        print('线程{}开始写入'.format(self.thread_id))
        with open('test' + self.thread_id + '.tmp', 'wb') as f:
            pass
        with open('test' + self.thread_id + '.tmp', 'ab+') as f:
            f.write(data)
        print('线程{}下载完成'.format(self.thread_id))


class MergeThread(Thread):
    def __init__(self, ):
        super(MergeThread, self).__init__()

    def run(self):
        pass


class MultiThreadDownload:
    def __init__(self, url, threads_num, ):
        pass


def isAlive(threads):
    for thread in threads:
        if thread.is_alive():
            return True
    return False


if __name__ == '__main__':
    threads = []
    threads_num = 4
    url = 'https://67ecedb6b9ec5e7a581d5a1c8c8aa0b3.dlied1.cdntips.net/dlied1.qq.com/qqweb/PCQQ/PCQQ_EXE/PCQQ2021.exe' \
          '?mkey=6097eed8716ca3c5&f=0000&cip=113.108.133.48&proto=https&access_type=$header_ApolloNet '
    final_path = url.split('?')[0].split('/')[-1]
    head_info = requests.head(url, headers=g.headers)
    file_size = int(head_info.headers['Content-Length'])
    g.sub_file_size = g.fileDivision(file_size, threads_num)
    for i in range(threads_num):
        thread = Download_Thread(url, i, g.sub_file_size[i], g.sub_file_size[i + 1])
        threads.append(thread)
    for i in range(threads_num):
        threads[i].start()
    while isAlive(threads):
        time.sleep(0.1)

    with open(final_path, 'wb') as final_file:
        for i in range(threads_num):
            with open('test' + str(i) + '.tmp', 'rb+') as f_tmp:
                final_file.write(f_tmp.read())
            os.remove('test' + str(i) + '.tmp')
