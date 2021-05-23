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
        self.headers = g.headers.copy()

    def run(self):
        start = time.time()
        self.headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        print('线程{}开始解析'.format(self.thread_id))
        print(self.headers)
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 206:
            data = r.content
            self.length = len(data)
            print('线程{}开始写入'.format(self.thread_id))
            with open('test' + self.thread_id + '.tmp', 'wb') as f:
                pass
            with open('test' + self.thread_id + '.tmp', 'ab+') as f:
                f.write(data)
            print('线程{}下载完成, 共用时{}s'.format(self.thread_id, time.time() - start))
        else:
            print('返回出错')


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
    url = 'http://upos-sz-mirrorcos.bilivideo.com/upgcxcode/36/19/341901936/341901936_nb2-1-80.flv?e' \
          '=ig8euxZM2rNcNbuHhbUVhoManWNBhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IMvXBvEuENvNCImNEVEua6m2jIxux0CkF6s2JZv5x0DQJZY2F8SkXKE9IB5QK==&deadline=1621771342&gen=playurl&nbs=1&oi=989425742&os=cosbv&platform=pc&trid=6a1d97e3d669492ea8976607d5a42fef&uipk=5&upsig=7fad4c874a7c0215dc54e81ac966a089&uparams=e,deadline,gen,nbs,oi,os,platform,trid,uipk&mid=0 '
    final_path = url.split('?')[0].split('/')[-1]
    start = time.time()
    head_info = requests.head(url, headers=g.headers)
    file_size = int(head_info.headers['Content-Length'])
    print(file_size)
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
            print(i)
            with open('test' + str(i) + '.tmp', 'rb+') as f_tmp:
                final_file.write(f_tmp.read())
            os.remove('test' + str(i) + '.tmp')
    print(time.time() - start)
