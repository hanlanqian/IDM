class GlobalsVariable:
    def __init__(self):
        self.BilibliHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Referer': 'https://space.bilibili.com/4899781/',
            'Origin': 'http://www.bilibili.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': '*/*',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': '*/*',
        }
        self.sub_file_size = []
        self.sub_file_download_percent = {}
        self.total_download = 0
        self.file_size = 0
        self.url = None
        self.filepath = None
        self.filename = None
        self.threads_num = None
        self.chunk_size = 1024 * 100
        self.Type = None
        # Bilibili
        self.BVid = None
        self.real_video_url = None


globals_variable = GlobalsVariable()