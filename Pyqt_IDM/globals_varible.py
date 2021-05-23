headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'https://space.bilibili.com/4899781/',
    'Origin': 'http://www.bilibili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}
sub_file_size = []


def fileDivision(filesize, threads_num):
    _sub_file_size = []
    unit = filesize / threads_num
    for i in range(threads_num):
        _sub_file_size.append(i * unit)
    _sub_file_size.append(filesize)
    return _sub_file_size
