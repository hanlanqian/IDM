#!/usr/bin/env python


from ..common import *

import re

# API key provided by cnbeining
appkey='85eb6835b0a1034e';
secretkey = '2ad42749773c441109bdc0191257a664'
client = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    #'User-Agent': 'Biligrab /0.8 (cnbeining@gmail.com)'
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36"
}

def get_srt_xml(id):
    url = 'http://comment.bilibili.com/%s.xml' % id
    return get_html(url)

def parse_srt_p(p):
    fields = p.split(',')
    assert len(fields) == 8, fields
    time, mode, font_size, font_color, pub_time, pool, user_id, history = fields
    time = float(time)

    mode = int(mode)
    assert 1 <= mode <= 8
    # mode 1~3: scrolling
    # mode 4: bottom
    # mode 5: top
    # mode 6: reverse?
    # mode 7: position
    # mode 8: advanced

    pool = int(pool)
    assert 0 <= pool <= 2
    # pool 0: normal
    # pool 1: srt
    # pool 2: special?

    font_size = int(font_size)

    font_color = '#%06x' % int(font_color)

    return pool, mode, font_size, font_color

def parse_srt_xml(xml):
    d = re.findall(r'<d p="([^"]+)">(.*)</d>', xml)
    for x, y in d:
        p = parse_srt_p(x)
    raise NotImplementedError()

def parse_cid_playurl(xml):
    from xml.dom.minidom import parseString
    try:
        doc = parseString(xml.encode('utf-8'))
        urls = [durl.getElementsByTagName('url')[0].firstChild.nodeValue for durl in doc.getElementsByTagName('durl')]
        return urls
    except:
        return []

