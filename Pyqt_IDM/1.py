import requests
import time
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'https://space.bilibili.com/4899781/',
    'Origin': 'http://www.bilibili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}
# headers.update({'Range': 'bytes=46787316-62383087'})
url = 'https://dldir1.qq.com/music/clntupate/QQMusicSetup.exe'
start = time.time()
res = requests.get(url, headers=headers, stream=True)
if res.status_code == 206 or res.status_code == 200:
    with open('QQMusicSetup.exe', 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print('success!')
    print(time.time()-start)
else:
    print('failed!')
