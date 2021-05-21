import requests
import re
from lxml import etree
import sys
import you_get

BVid = 'BV1Q64y1d7xo'
sys.argv = ['you-get', 'https://www.bilibili.com/video/{}'.format(BVid)]
video_urls = you_get.main()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'https://space.bilibili.com/4899781/',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}
r = requests.get(video_urls[0], headers=headers)
with open('{}.flv'.format(BVid), "wb") as f:
    f.write(r.content)
print("download finished!")
