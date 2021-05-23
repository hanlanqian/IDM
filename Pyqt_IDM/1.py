import requests


res = requests.head('https://www.bilibili.com')
print(res.headers)