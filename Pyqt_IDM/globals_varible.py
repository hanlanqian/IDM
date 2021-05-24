headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'https://space.bilibili.com/4899781/',
    'Origin': 'http://www.bilibili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': '*/*',
}
sub_file_size = []
sub_file_download = {}
sub_file_download_percent = {}
total_download = 0
file_size = 0
chunk_size = 1024 * 50


def fileDivision(filesize, threads_num):
    _sub_file_size = []
    unit = filesize // threads_num
    for i in range(threads_num):
        _sub_file_size.append(i * unit)
    _sub_file_size.append(filesize)
    return _sub_file_size
