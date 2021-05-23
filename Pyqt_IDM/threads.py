from threading import Thread, Lock
import time
import requests
import globals_varible as g
import os
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
        r = session.get(self.url, headers=self.headers)
        data = r.content
        if r.status_code == 206:
            print('线程{}开始写入'.format(self.thread_id))
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'wb') as f:
                pass
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'ab+') as f:
                f.write(data)
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
        with open(self.filepath+self.filename, 'ab+') as final_file:
            with open(self.filepath + self.filename + self.thread_id + '.tmp', 'rb+') as file_tmp:
                final_file.write(file_tmp.read())
            os.remove(self.file_path + self.filename + self.thread_id + '.tmp')
        thread_lock.release()


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
        head_info = session.head(self.url, headers=g.headers)
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

        # with open(self.file_path + self.filename, 'wb') as final_file:
        #     for i in range(threads_num):
        #         with open(self.file_path + self.filename + str(i) + '.tmp', 'rb+') as f_tmp:
        #             final_file.write(f_tmp.read())
        #         os.remove(self.file_path + self.filename + str(i) + '.tmp')
        for i in range(threads_num):
            MergeThread(self.file_path, self.filename, i).start()

        print(time.time() - start_time)


def isAlive(threads):
    for thread in threads:
        if thread.is_alive():
            return True
    return False


if __name__ == '__main__':
    threads_num = 6
    # url = 'http://upos-sz-mirrorkodo.bilivideo.com/upgcxcode/72/95/325839572/325839572-1-80.flv?e=ig8euxZM2rNcNbUjhbUVhoMB7bNBhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IMvXBvEuENvNCImNEVEua6m2jIxux0CkF6s2JZv5x0DQJZY2F8SkXKE9IB5QK==&deadline=1621781373&gen=playurl&nbs=1&oi=989425742&os=kodobv&platform=pc&trid=d03db4416f334943ab950e989bde4af8&uipk=5&upsig=eb6dc39ce50a52aebe521c4e06638f3b&uparams=e,deadline,gen,nbs,oi,os,platform,trid,uipk&mid=0'
    url = 'http://upos-sz-mirrorkodo.bilivideo.com/upgcxcode/72/95/325839572/325839572-1-80.flv?e=ig8euxZM2rNcNbUjhbUVhoMB7bNBhwdEto8g5X10ugNcXBlqNxHxNEVE5XREto8KqJZHUa6m5J0SqE85tZvEuENvNC8xNEVE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IMvXBvEuENvNCImNEVEua6m2jIxux0CkF6s2JZv5x0DQJZY2F8SkXKE9IB5QK==&deadline=1621798122&gen=playurl&nbs=1&oi=989425742&os=kodobv&platform=pc&trid=3f1b653d15114c58a19af2b40f30194d&uipk=5&upsig=0fb06d3628e11f7bc35fd4590f7e61d4&uparams=e,deadline,gen,nbs,oi,os,platform,trid,uipk&mid=0'
    mutil_download = MultiThreadDownload(url, threads_num)
    mutil_download.start()
    # mutil_download.join()
