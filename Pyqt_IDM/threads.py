from threading import Thread, Lock
from PyQt5.QtCore import QThread, pyqtSignal
import time
import requests
import globals_varible as g
import os
import you_get
import sys

thread_lock = Lock()
session = requests.session()


class Download_Thread(QThread):
    download_info_signal = pyqtSignal(str, float)

    def __init__(self, thread_id, start_bytes, end_bytes):
        super(Download_Thread, self).__init__()
        self.thread_id = str(thread_id)
        self.start_bytes = start_bytes
        self.end_bytes = end_bytes - 1
        self.headers = g.headers.copy()

    def run(self):
        start = time.time()
        self.headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        self.download_info_signal.emit('线程{}开始解析'.format(self.thread_id), 0.0)
        r = session.get(g.url, headers=self.headers, stream=True)
        self.download_info_signal.emit('线程{}解析用时{}'.format(self.thread_id, time.time() - start), 0.0)
        if r.status_code == 206 or r.status_code == 200:
            self.download_info_signal.emit('线程{}开始写入'.format(self.thread_id), 0.0)
            with open(g.filepath + g.filename + self.thread_id + '.tmp', 'wb') as f:
                pass
            with open(g.filepath + g.filename + self.thread_id + '.tmp', 'ab+') as f:
                for chunk in r.iter_content(chunk_size=g.chunk_size):
                    f.write(chunk)
                    g.sub_file_download[self.thread_id] += g.chunk_size
                    percent = g.chunk_size / (self.end_bytes - self.start_bytes)
                    g.sub_file_download_percent['线程' + self.thread_id] += percent * 100
                    g.total_download += g.chunk_size
                    self.download_info_signal.emit(str(g.sub_file_download_percent), g.total_download)
            self.download_info_signal.emit('线程{}下载完成, 共用时{}s'.format(self.thread_id, time.time() - start), 0.0)
        else:
            self.download_info_signal.emit('get请求出错', 0.0)


class MergeThread(Thread):
    def __init__(self, thread_id):
        super(MergeThread, self).__init__()
        self.thread_id = str(thread_id)

    def run(self):
        thread_lock.acquire()
        with open(g.filepath + g.filename, 'ab+') as final_file:
            with open(g.filepath + g.filename + self.thread_id + '.tmp', 'rb+') as file_tmp:
                final_file.write(file_tmp.read())
            os.remove(g.filepath + g.filename + self.thread_id + '.tmp')
        thread_lock.release()


class MultiThreadDownload(QThread):
    download_info_signal = pyqtSignal(str, float)

    def __init__(self, show_download_info):
        super(MultiThreadDownload, self).__init__()
        self.show_download_info = show_download_info
        self.threads = []

    def run(self):
        if g.Type == 'Bilibili':
            self.download_info_signal.emit('根据BV号下载视频：\n正在解析视频链接', 0.0)
            sys.argv = ['you-get', 'https://www.bilibili.com/video/' + g.BVid]
            g.url = you_get.main()[0]
            g.filename = 'Bilibili视频' + g.url.split('?')[0].split('/')[-1]
            self.download_info_signal.emit('已获得真实视频链接，准备开始下载', 0.0)
        self.download_info_signal.emit('开始解析连接', 0.0)
        # print('开始解析连接')
        start_time = time.time()
        head_info = session.head(g.url, headers=g.headers)
        g.file_size = int(head_info.headers['Content-Length'])
        sub_file_size = fileDivision(g.file_size, g.threads_num)
        # print('该文件大小为{}kb, 共用时{}s'.format(g.file_size / 1024, time.time() - start_time))
        self.download_info_signal.emit('该文件大小为{}kb, 共用时{}s'.format(g.file_size / 1024, time.time() - start_time), 0.0)
        with open(g.filepath + g.filename, 'wb') as f:
            pass
        for i in range(g.threads_num):
            g.sub_file_download.update({str(i): 0})
            g.sub_file_download_percent.update({'线程' + str(i): 0})
            thread = Download_Thread(i, sub_file_size[i], sub_file_size[i + 1])
            thread.download_info_signal.connect(self.show_download_info)
            thread.start()
            self.threads.append(thread)
        while isAlive(self.threads):
            time.sleep(0.1)
        for i in range(g.threads_num):
            MergeThread(i).start()
        total_time = time.time() - start_time
        # print(f'一共耗时{total_time:.2f}s, 平均下载速度为{g.file_size / 1024 / 1024 / total_time:.4f}MB/s')
        self.download_info_signal.emit(
            f'一共耗时{total_time:.2f}s, 平均下载速度为{g.file_size / 1024 / 1024 / total_time:.4f}MB/s', 0.0)

    def stop(self):
        for thread in self.threads:
            thread.terminate()
        self.terminate()


class ParseVideoLink(QThread):
    download_info_signal = pyqtSignal(str)

    def __init__(self, show_download_info):
        super(ParseVideoLink, self).__init__()
        self.show_download_info = show_download_info

    def run(self):
        self.download_info_signal.emit('正在解析视频链接')
        sys.argv = ['you-get', 'https://www.bilibili.com/video/' + g.BVid]
        g.url = you_get.main()[0]
        g.filename = 'Bilibili视频' + g.url.split('?')[0].split('/')[-1]
        self.download_info_signal.emit('已获得真实视频链接，准备开始下载')


def isAlive(threads):
    for thread in threads:
        if thread.isRunning():
            return True
    return False


def fileDivision(filesize, threads_num):
    _sub_file_size = []
    unit = filesize // threads_num
    for i in range(threads_num):
        _sub_file_size.append(i * unit)
    _sub_file_size.append(filesize)
    return _sub_file_size


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
