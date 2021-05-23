import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'https://space.bilibili.com/4899781/',
    'Origin': 'http://www.bilibili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}
headers.update({'Range': 'bytes=1010-2228'})
print(headers)
url = 'https://67ecedb6b9ec5e7a581d5a1c8c8aa0b3.dlied1.cdntips.net/dlied1.qq.com/qqweb/PCQQ/PCQQ_EXE/PCQQ2021.exe' \
      '?mkey=6097eed8716ca3c5&f=0000&cip=113.108.133.48&proto=https&access_type=$header_ApolloNet '
res = requests.get(url, headers=headers)
if res.status_code == 206:
    with open('test', 'wb') as f:
        f.write(res.content)
    print('success!')
else:
    print('failed!')