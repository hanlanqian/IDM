from threading import Thread, Lock
import time
import requests
import globals_varible as g
import os
import you_get
import sys
from PyQt5.QtCore import QThread

thread_lock = Lock()
session = requests.session()


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
        r = session.get(self.url, headers=self.headers, stream=True)
        print('线程{}解析用时{}'.format(self.thread_id, time.time() - start))
        if r.status_code == 206 or r.status_code == 200:
            print('线程{}开始写入'.format(self.thread_id))
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'wb') as f:
                pass
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'ab+') as f:
                for chunk in r.iter_content(chunk_size=g.chunk_size):
                    f.write(chunk)
                    g.sub_file_download[self.thread_id] += g.chunk_size
                    percent = g.chunk_size/(g.sub_file_size[int(self.thread_id)+1]-g.sub_file_size[int(self.thread_id)])
                    g.sub_file_download_percent['线程'+self.thread_id] += percent*100
                    g.total_download += g.chunk_size
            print('线程{}下载完成, 共用时{}s'.format(self.thread_id, time.time() - start))
        else:
            print('get请求出错')


class MergeThread(Thread):
    def __init__(self, filepath, filename, thread_id):
        super(MergeThread, self).__init__()
        self.filepath = filepath
        self.filename = filename
        self.thread_id = str(thread_id)

    def run(self):
        thread_lock.acquire()  # 加个同步锁就好了
        with open(self.filepath + self.filename, 'ab+') as final_file:
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'rb+') as file_tmp:
                final_file.write(file_tmp.read())
            os.remove(self.filepath + self.filename + self.thread_id + '.tmp')
        thread_lock.release()


class MultiThreadDownload(Thread):
    def __init__(self, url, threads_num, file_path='./'):
        super(MultiThreadDownload, self).__init__()
        self.url = url
        self.threads_num = threads_num
        self.file_path = file_path
        self.threads = []
        self.filename = url.split('?')[0].split('/')[-1]

    def run(self):
        print('开始解析连接')
        start_time = time.time()
        head_info = session.head(self.url, headers=g.headers)
        g.file_size = int(head_info.headers['Content-Length'])
        g.sub_file_size = g.fileDivision(g.file_size, self.threads_num)
        print('该文件大小为{}kb, 共用时{}s'.format(g.file_size / 1024, time.time() - start_time))
        with open(self.file_path + self.filename, 'wb') as f:
            pass
        for i in range(threads_num):
            g.sub_file_download.update({str(i): 0})
            g.sub_file_download_percent.update({'线程'+str(i): 0})
            thread = Download_Thread(url, self.file_path, self.filename, i, g.sub_file_size[i],
                                     g.sub_file_size[i + 1])
            self.threads.append(thread)
        for i in range(threads_num):
            self.threads[i].start()
        Thread(target=show).start()
        while isAlive(self.threads):
            time.sleep(0.1)
        for i in range(threads_num):
            MergeThread(self.file_path, self.filename, i).start()
        total_time = time.time() - start_time
        print(f'一共耗时{total_time:.2f}s, 平均下载速度为{g.file_size/1024/1024/total_time:.4f}MB/s')


def isAlive(threads):
    for thread in threads:
        if thread.is_alive():
            return True
    return False


def show():
    while True:
        time.sleep(1)
        if g.total_download >= g.file_size:
            break
        # for thread, percent in g.sub_file_download_percent.items():
        #     print(thread + ':' + f'{percent:.4f}', end='\t')
        print(g.sub_file_download_percent)


if __name__ == '__main__':
    Bilibili = False
    if Bilibili:
        # 输入视频bv号
        BVid = 'BV1Fr4y1N7ah'
        sys.argv = ['you-get', 'https://www.bilibili.com/video/{}'.format(BVid)]
        start = time.time()
        # 调取自定义更改后的you_get库获取对应视频链接
        url = you_get.main()[0]
    else:
        url = 'https://dldir1.qq.com/music/clntupate/QQMusicSetup.exe'
    threads_num = 4
    mainthread = MultiThreadDownload(url, threads_num)
    mainthread.start()
