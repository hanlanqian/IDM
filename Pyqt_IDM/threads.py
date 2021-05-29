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
    download_info_signal = pyqtSignal(dict)

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
        self.download_info_signal.emit({'info': '线程{}开始解析'.format(self.thread_id)})
        r = session.get(g.globals_variable.url, headers=self.headers, stream=True)
        self.download_info_signal.emit({'info': '线程{}解析用时{}'.format(self.thread_id, time.time() - start)})
        if r.status_code == 206 or r.status_code == 200:
            self.download_info_signal.emit({'info': '线程{}开始写入'.format(self.thread_id)})
            with open(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp', 'ab+') as f:
                files.append(f)
                for chunk in r.iter_content(chunk_size=g.globals_variable.chunk_size):
                    while self.PauseFlag:
                        time.sleep(0.1)
                    f.write(chunk)
                    percent = g.globals_variable.chunk_size / (self.end_bytes - self.start_bytes)
                    g.globals_variable.sub_file_download_percent['线程' + self.thread_id] += percent * 100
                    g.globals_variable.total_download += g.globals_variable.chunk_size
                    self.download_info_signal.emit({'sub_downloaded': g.globals_variable.sub_file_download_percent,
                                                    'downloaded': g.globals_variable.total_download})
            self.download_info_signal.emit({'info': '线程{}下载完成, 共用时{}s'.format(self.thread_id, time.time() - start)})


class MergeThread(Thread):
    def __init__(self, thread_id):
        super(MergeThread, self).__init__()
        self.thread_id = str(thread_id)

    def run(self):
        thread_lock.acquire()
        if os.path.exists(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp'):
            with open(g.globals_variable.filepath + g.globals_variable.filename, 'ab+') as final_file:
                with open(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp',
                          'rb+') as file_tmp:
                    final_file.write(file_tmp.read())
                os.remove(g.globals_variable.filepath + g.globals_variable.filename + self.thread_id + '.tmp')
        thread_lock.release()


class MultiThreadDownload(QThread):
    download_info_signal = pyqtSignal(dict)

    def __init__(self, show_download_info):
        super(MultiThreadDownload, self).__init__()
        self.show_download_info = show_download_info
        self.threads = []
        self.VideoFlag = True
        self.VideoMultiFlag = True

    def run(self):
        if g.globals_variable.Type == 'Bilibili':
            self.download_info_signal.emit({'info': '根据BV号下载视频：\n正在解析视频链接',
                                            })
            site.url = 'https://www.bilibili.com/video/' + g.globals_variable.BVid
            site.prepare()
            if len(site.real_urls) < 1:
                self.download_info_signal.emit({
                    'info': '你输入的BV号对应的视频有多个分P，暂不支持下载',
                    'value': -1
                })
                self.VideoMultiFlag = False
                self.VideoFlag = False
                self.stop()
                self.download_info_signal.emit({'info': "已停止下载"})
            else:
                g.globals_variable.url = site.real_urls[0]
                g.globals_variable.filename = 'Bilibili视频' + g.globals_variable.BVid + '.' + \
                                              g.globals_variable.url.split('?')[0].split('/')[-1].split('.')[-1]
                self.download_info_signal.emit({'info': '已获得真实视频链接，准备开始下载',
                                                })
        if self.VideoMultiFlag:
            self.download_info_signal.emit({'info': '开始解析连接',
                                            })
            start_time = time.time()
            head_info = session.head(g.globals_variable.url, headers=g.globals_variable.headers)
            g.globals_variable.file_size = int(head_info.headers['Content-Length'])
            if g.globals_variable.Type == 'Bilibili' and g.globals_variable.file_size < 1024:
                self.download_info_signal.emit({'info': '视频链接失效，即将退出下载！',
                                                })
                self.VideoFlag = False
                self.stop()
                self.download_info_signal.emit({'info': "已停止下载",
                                                'value': 1.0,
                                                })
            if self.VideoFlag:
                with open(g.globals_variable.filepath + g.globals_variable.filename, 'wb') as f:
                    files.append(f)
                    pass
            sub_file_size = fileDivision(g.globals_variable.file_size, g.globals_variable.threads_num)
            self.download_info_signal.emit(
                {'info': '该文件大小为{}kb, 共用时{}s'.format(g.globals_variable.file_size / 1024, time.time() - start_time),
                 })
            for i in range(g.globals_variable.threads_num):
                g.globals_variable.sub_file_download_percent.update({'线程' + str(i): 0})
                thread = Download_Thread(i, sub_file_size[i], sub_file_size[i + 1])
                thread.download_info_signal.connect(self.show_download_info)
                thread.start()
                self.threads.append(thread)
            while isAlive(self.threads):
                time.sleep(0.1)
            for i in range(g.globals_variable.threads_num):
                MergeThread(i).start()
            total_time = time.time() - start_time
            self.download_info_signal.emit(
                {
                    'info': f'一共耗时{total_time:.2f}s, 平均下载速度为{g.globals_variable.file_size / 1024 / 1024 / total_time:.4f}MB/s',
                    })
        else:
            pass

    def pause(self):
        for thread in self.threads:
            thread.PauseFlag = not thread.PauseFlag
        self.download_info_signal.emit({'info': "程序已暂停/继续！"})

    def stop(self):
        # 暂停下载后会关闭已打开文件并删除已经下载的文件
        for file in files:
            file.close()
        for thread in self.threads:
            thread.terminate()
        if self.VideoFlag and self.VideoMultiFlag:
            os.remove(g.globals_variable.filepath + g.globals_variable.filename)
        if self.VideoFlag:
            for i in range(g.globals_variable.threads_num):
                os.remove(g.globals_variable.filepath + g.globals_variable.filename + str(i) + '.tmp')

    def generate_log(self):
        pass
