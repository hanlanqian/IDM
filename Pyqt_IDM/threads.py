from threading import Thread, Lock
import time
import requests
import globals_varible as g
import os
from PyQt5.QtCore import QThread


class Download_Thread(Thread):
    def __init__(self, url, filepath, filename, thread_id, start_bytes, end_bytes):
        super(Download_Thread, self).__init__()
        self.url = url
        self.filepath = filepath
        self.filename = filename
        self.thread_id = str(thread_id)
        self.start_bytes = start_bytes
        self.end_bytes = end_bytes - 1
        self.headers = g.headers.copy()

    def run(self):
        start = time.time()
        self.headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        print('线程{}开始解析'.format(self.thread_id))
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 206:
            print('线程{}开始写入'.format(self.thread_id))
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'wb') as f:
                pass
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'ab+') as f:
                f.write(r.content)
            print('线程{}下载完成, 共用时{}s'.format(self.thread_id, time.time() - start))
        else:
            print('get请求出错')


class MergeThread(Thread):
    def __init__(self, url, threads_num, file_path, ):
        super(MergeThread, self).__init__()

    def run(self):
        pass


class MultiThreadDownload(Thread):
    def __init__(self, url, threads_num, file_path='./'):
        super(MultiThreadDownload, self).__init__()
        self.url = url
        self.threads_num = threads_num
        self.file_path = file_path
        self.threads = []
        self.filename = url.split('?')[0].split('/')[-1]
        self.file_size = None
        self.sub_file_size = []

    def run(self):
        print('开始解析连接')
        start_time = time.time()
        head_info = requests.head(self.url, headers=g.headers)
        self.file_size = int(head_info.headers['Content-Length'])
        self.sub_file_size = g.fileDivision(self.file_size, self.threads_num)
        print('该文件大小为{}kb'.format(self.file_size/1024))
        for i in range(threads_num):
            thread = Download_Thread(url, self.file_path, self.filename, i, self.sub_file_size[i],
                                     self.sub_file_size[i + 1])
            self.threads.append(thread)
        for i in range(threads_num):
            self.threads[i].start()
        while isAlive(self.threads):
            time.sleep(0.1)

        with open(self.file_path + self.filename, 'wb') as final_file:
            for i in range(threads_num):
                print(i)
                with open(self.file_path + self.filename + str(i) + '.tmp', 'rb+') as f_tmp:
                    final_file.write(f_tmp.read())
                os.remove(self.file_path + self.filename + str(i) + '.tmp')
        print(time.time() - start_time)


def isAlive(threads):
    for thread in threads:
        if thread.is_alive():
            return True
    return False


if __name__ == '__main__':
    threads_num = 4
    # url = 'http://upos-sz-mirrorcos.bilivideo.com/upgcxcode/36/19/341901936/341901936_nb2-1-80.flv?e' \
    #       '=ig8euxZM2rNcNbuHhbUVhoManWNBhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IMvXBvEuENvNCImNEVEua6m2jIxux0CkF6s2JZv5x0DQJZY2F8SkXKE9IB5QK==&deadline=1621771342&gen=playurl&nbs=1&oi=989425742&os=cosbv&platform=pc&trid=6a1d97e3d669492ea8976607d5a42fef&uipk=5&upsig=7fad4c874a7c0215dc54e81ac966a089&uparams=e,deadline,gen,nbs,oi,os,platform,trid,uipk&mid=0 '
    url = 'https://67ecedb6b9ec5e7a581d5a1c8c8aa0b3.dlied1.cdntips.net/dlied1.qq.com/qqweb/PCQQ/PCQQ_EXE/PCQQ2021.exe'
    mutil_download = MultiThreadDownload(url, threads_num)
    mutil_download.start()
    # mutil_download.join()
