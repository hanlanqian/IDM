import requests
import re
import time
import sys
import you_get

BVid = 'BV1TB4y1A7nL'
sys.argv = ['you-get', 'https://www.bilibili.com/video/{}'.format(BVid)]
start = time.time()
video_urls = you_get.main()
print(time.time()-start)
print(video_urls[0]['src'])

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'https://space.bilibili.com/4899781/',
    'Origin': 'http://www.bilibili.com',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

start = time.time()
r = requests.get(video_urls[0]['src'][0], headers=headers)
# r = requests.get('https://cn-gdgz-fx-bcache-03.bilivideo.com/upgcxcode/59/43/250424359/250424359_nb2-1-16.mp4?e=ig8euxZM2rNcNbuVhwdVtWuVhwdVNEVEuCIv29hEn0lqXg8Y2ENvNCImNEVEUJ1miI7MT96fqj3E9r1qNCNEtodEuxTEtodE9EKE9IMvXBvE2ENvNCImNEVEK9GVqJIwqa80WXIekXRE9IMvXBvEuENvNCImNEVEua6m2jIxux0CkF6s2JZv5x0DQJZY2F8SkXKE9IB5QK==&uipk=5&nbs=1&deadline=1621627283&gen=playurlv2&os=bcache&oi=989425742&trid=000090a5b2de0081423d9d6e107fba417d88u&platform=pc&upsig=725d8af9287224aa3df77a7eac9a9451&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,platform&cdnid=3803&mid=37850911&bvc=vod&orderid=0,3&agrr=1&logo=80000000', headers=headers)
print(time.time()-start)

start = time.time()
with open('{}.flv'.format(BVid), "wb") as f:
    f.write(r.content)
print(time.time()-start)
print("download finished!")
