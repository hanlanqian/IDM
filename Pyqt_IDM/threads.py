from threading import Thread, Lock
from PyQt5.QtCore import QThread, pyqtSignal
from you_get.extractors.bilibili import site
import time
import requests
import globals_variable as g
import os


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


thread_lock = Lock()
session = requests.session()
files = []


class Download_Thread(QThread):
    download_info_signal = pyqtSignal(str, float)

    def __init__(self, thread_id, start_bytes, end_bytes):
        super(Download_Thread, self).__init__()
        self.thread_id = str(thread_id)
        self.start_bytes = start_bytes
        self.end_bytes = end_bytes - 1
        self.headers = g.globals_variable.headers.copy()
        self.PauseFlag = False
        self.StopFlag = False

    def run(self):
        start = time.time()
        self.headers.update({'Range': 'bytes={}-{}'.format(self.start_bytes, self.end_bytes)})
        self.download_info_signal.emit('线程{}开始解析'.format(self.thread_id), 0.0)
        r = session.get(g.globals_variable.url, headers=self.headers, stream=True)
        self.download_info_signal.emit('线程{}解析用时{}'.format(self.thread_id, time.time() - start), 0.0)
        if r.status_code == 206 or r.status_code == 200:
            self.download_info_signal.emit('线程{}开始写入'.format(self.thread_id), 0.0)
            with open(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp', 'ab+') as f:
                files.append(f)
                for chunk in r.iter_content(chunk_size=g.globals_variable.chunk_size):
                    while self.PauseFlag:
                        time.sleep(0.1)
                    f.write(chunk)
                    percent = g.globals_variable.chunk_size / (self.end_bytes - self.start_bytes)
                    g.globals_variable.sub_file_download_percent['线程' + self.thread_id] += percent * 100
                    g.globals_variable.total_download += g.globals_variable.chunk_size
                    self.download_info_signal.emit(str(g.globals_variable.sub_file_download_percent),
                                                   g.globals_variable.total_download)
            self.download_info_signal.emit('线程{}下载完成, 共用时{}s'.format(self.thread_id, time.time() - start), 0.0)
        else:
            self.download_info_signal.emit('get请求出错', 0.0)


class MergeThread(Thread):
    def __init__(self, thread_id):
        super(MergeThread, self).__init__()
        self.thread_id = str(thread_id)

    def run(self):
        thread_lock.acquire()
        with open(g.globals_variable.filepath + g.globals_variable.filename, 'ab+') as final_file:
            with open(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp',
                      'rb+') as file_tmp:
                final_file.write(file_tmp.read())
            os.remove(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp')
        thread_lock.release()


class MultiThreadDownload(QThread):
    download_info_signal = pyqtSignal(str, float)

    def __init__(self, show_download_info):
        super(MultiThreadDownload, self).__init__()
        self.show_download_info = show_download_info
        self.threads = []
        self.Flag = True

    def run(self):
        if g.globals_variable.Type == 'Bilibili':
            self.download_info_signal.emit('根据BV号下载视频：\n正在解析视频链接', 0.0)
            site.url = 'https://www.bilibili.com/video/' + g.globals_variable.BVid
            site.prepare()
            g.globals_variable.url = site.real_urls[0]
            g.globals_variable.filename = 'Bilibili视频' + g.globals_variable.BVid + '.' + \
                                          g.globals_variable.url.split('?')[0].split('/')[-1].split('.')[-1]
            self.download_info_signal.emit('已获得真实视频链接，准备开始下载', 0.0)
        self.download_info_signal.emit('开始解析连接', 0.0)
        start_time = time.time()
        head_info = session.head(g.globals_variable.url, headers=g.globals_variable.headers)
        g.globals_variable.file_size = int(head_info.headers['Content-Length'])
        if g.globals_variable.Type == 'Bilibili' and g.globals_variable.file_size < 1024:
            self.download_info_signal.emit('获取真实链接失败，即将退出下载！', 0.0)
            self.Flag = False
            self.stop()
            self.download_info_signal.emit("已停止下载", -1.0)
        sub_file_size = fileDivision(g.globals_variable.file_size, g.globals_variable.threads_num)
        self.download_info_signal.emit(
            '该文件大小为{}kb, 共用时{}s'.format(g.globals_variable.file_size / 1024, time.time() - start_time), 0.0)
        with open(g.globals_variable.filepath + g.globals_variable.filename, 'wb') as f:
            files.append(f)
            pass
        for i in range(g.globals_variable.threads_num):
            g.globals_variable.sub_file_download_percent.update({'线程' + str(i): 0})
            thread = Download_Thread(i, sub_file_size[i], sub_file_size[i + 1])
            thread.download_info_signal.connect(self.show_download_info)
            thread.start()
            self.threads.append(thread)
        while isAlive(self.threads) and self.threads[-1].StopFlag == False:
            time.sleep(0.1)
        for i in range(g.globals_variable.threads_num):
            MergeThread(i).start()
        total_time = time.time() - start_time
        self.download_info_signal.emit(
            f'一共耗时{total_time:.2f}s, 平均下载速度为{g.globals_variable.file_size / 1024 / 1024 / total_time:.4f}MB/s', 0.0)

    def pause(self):




    def stop(self):
        # 暂停下载后会关闭已打开文件并删除已经下载的文件
        for file in files:
            file.close()
        for thread in self.threads:
            thread.terminate()
        os.remove(g.globals_variable.filepath + g.globals_variable.filename)
        if self.Flag:
            for i in range(g.globals_variable.threads_num):
                os.remove(g.globals_variable.filepath + g.globals_variable.filename + str(i) + '.tmp')
        self.terminate()
