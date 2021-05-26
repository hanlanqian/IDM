#!/usr/bin/env python
import io
import re
import sys
import json
import locale
import logging
import ssl
import zlib
from io import BytesIO
import gzip
from urllib import request, parse



sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

SITES = {
    '163': 'netease',
    '56': 'w56',
    '365yg': 'toutiao',
    'acfun': 'acfun',
    'archive': 'archive',
    'baidu': 'baidu',
    'bandcamp': 'bandcamp',
    'baomihua': 'baomihua',
    'bigthink': 'bigthink',
    'bilibili': 'bilibili',
    'cctv': 'cntv',
    'cntv': 'cntv',
    'cbs': 'cbs',
    'coub': 'coub',
    'dailymotion': 'dailymotion',
    'douban': 'douban',
    'douyin': 'douyin',
    'douyu': 'douyutv',
    'ehow': 'ehow',
    'facebook': 'facebook',
    'fc2': 'fc2video',
    'flickr': 'flickr',
    'freesound': 'freesound',
    'fun': 'funshion',
    'google': 'google',
    'giphy': 'giphy',
    'heavy-music': 'heavymusic',
    'huomao': 'huomaotv',
    'iask': 'sina',
    'icourses': 'icourses',
    'ifeng': 'ifeng',
    'imgur': 'imgur',
    'in': 'alive',
    'infoq': 'infoq',
    'instagram': 'instagram',
    'interest': 'interest',
    'iqilu': 'iqilu',
    'iqiyi': 'iqiyi',
    'ixigua': 'ixigua',
    'isuntv': 'suntv',
    'iwara': 'iwara',
    'joy': 'joy',
    'kankanews': 'bilibili',
    'kakao': 'kakao',
    'khanacademy': 'khan',
    'ku6': 'ku6',
    'kuaishou': 'kuaishou',
    'kugou': 'kugou',
    'kuwo': 'kuwo',
    'le': 'le',
    'letv': 'le',
    'lizhi': 'lizhi',
    'longzhu': 'longzhu',
    'lrts': 'lrts',
    'magisto': 'magisto',
    'metacafe': 'metacafe',
    'mgtv': 'mgtv',
    'miomio': 'miomio',
    'missevan': 'missevan',
    'mixcloud': 'mixcloud',
    'mtv81': 'mtv81',
    'miaopai': 'yixia',
    'naver': 'naver',
    '7gogo': 'nanagogo',
    'nicovideo': 'nicovideo',
    'pinterest': 'pinterest',
    'pixnet': 'pixnet',
    'pptv': 'pptv',
    'qingting': 'qingting',
    'qq': 'qq',
    'showroom-live': 'showroom',
    'sina': 'sina',
    'smgbb': 'bilibili',
    'sohu': 'sohu',
    'soundcloud': 'soundcloud',
    'ted': 'ted',
    'theplatform': 'theplatform',
    'tiktok': 'tiktok',
    'tucao': 'tucao',
    'tudou': 'tudou',
    'tumblr': 'tumblr',
    'twimg': 'twitter',
    'twitter': 'twitter',
    'ucas': 'ucas',
    'vimeo': 'vimeo',
    'wanmen': 'wanmen',
    'weibo': 'miaopai',
    'veoh': 'veoh',
    'vine': 'vine',
    'vk': 'vk',
    'xiaokaxiu': 'yixia',
    'xiaojiadianvideo': 'fc2video',
    'ximalaya': 'ximalaya',
    'xinpianchang': 'xinpianchang',
    'yizhibo': 'yizhibo',
    'youku': 'youku',
    'youtu': 'youtube',
    'youtube': 'youtube',
    'zhanqi': 'zhanqi',
    'zhibo': 'zhibo',
    'zhihu': 'zhihu',
}

dry_run = False
json_output = False
force = False
skip_existing_file_size_check = False
player = None
extractor_proxy = None
cookies = None
output_filename = None
auto_rename = False
insecure = False

fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  # noqa
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43',
    # noqa
}

if sys.stdout.isatty():
    default_encoding = sys.stdout.encoding.lower()
else:
    default_encoding = locale.getpreferredencoding().lower()


def rc4(key, data):
    # all encryption algo should work on bytes
    assert type(key) == type(data) and type(key) == type(b'')
    state = list(range(256))
    j = 0
    for i in range(256):
        j += state[i] + key[i % len(key)]
        j &= 0xff
        state[i], state[j] = state[j], state[i]

    i = 0
    j = 0
    out_list = []
    for char in data:
        i += 1
        i &= 0xff
        j += state[i]
        j &= 0xff
        state[i], state[j] = state[j], state[i]
        prn = state[(state[i] + state[j]) & 0xff]
        out_list.append(char ^ prn)

    return bytes(out_list)


def general_m3u8_extractor(url, headers={}):
    m3u8_list = get_content(url, headers=headers).split('\n')
    urls = []
    for line in m3u8_list:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.startswith('http'):
                urls.append(line)
            else:
                seg_url = parse.urljoin(url, line)
                urls.append(seg_url)
    return urls


def maybe_print(*s):
    try:
        print(*s)
    except:
        pass


def tr(s):
    if default_encoding == 'utf-8':
        return s
    else:
        return s
        # return str(s.encode('utf-8'))[2:-1]


# DEPRECATED in favor of match1()
def r1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)


# DEPRECATED in favor of match1()
def r1_of(patterns, text):
    for p in patterns:
        x = r1(p, text)
        if x:
            return x


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


def matchall(text, patterns):
    """Scans through a string for substrings matched some patterns.

    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.

    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret




def parse_query_param(url, param):
    """Parses the query string of a URL and returns the value of a parameter.

    Args:
        url: A URL.
        param: A string representing the name of the parameter.

    Returns:
        The value of the parameter.
    """

    try:
        return parse.parse_qs(parse.urlparse(url).query)[param][0]
    except:
        return None


def unicodize(text):
    return re.sub(
        r'\\u([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])',
        lambda x: chr(int(x.group(0)[2:], 16)),
        text
    )


# DEPRECATED in favor of util.legitimize()
def escape_file_path(path):
    path = path.replace('/', '-')
    path = path.replace('\\', '-')
    path = path.replace('*', '-')
    path = path.replace('?', '-')
    return path


def ungzip(data):
    """Decompresses data for Content-Encoding: gzip.
    """
    buffer = BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()


def undeflate(data):
    """Decompresses data for Content-Encoding: deflate.
    (the zlib compression is used.)
    """
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data) + decompressobj.flush()


# DEPRECATED in favor of get_content()
def get_response(url, faker=False):
    logging.debug('get_response: %s' % url)

    # install cookies
    if cookies:
        opener = request.build_opener(request.HTTPCookieProcessor(cookies))
        request.install_opener(opener)

    if faker:
        response = request.urlopen(
            request.Request(url, headers=fake_headers), None
        )
    else:
        response = request.urlopen(url)

    data = response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        data = ungzip(data)
    elif response.info().get('Content-Encoding') == 'deflate':
        data = undeflate(data)
    response.data = data
    return response


# DEPRECATED in favor of get_content()
def get_html(url, encoding=None, faker=False):
    content = get_response(url, faker).data
    return str(content, 'utf-8', 'ignore')


# DEPRECATED in favor of get_content()
def get_decoded_html(url, faker=False):
    response = get_response(url, faker)
    data = response.data
    charset = r1(r'charset=([\w-]+)', response.headers['content-type'])
    if charset:
        return data.decode(charset, 'ignore')
    else:
        return data


def get_location(url, headers=None, get_method='HEAD'):
    logging.debug('get_location: %s' % url)

    if headers:
        req = request.Request(url, headers=headers)
    else:
        req = request.Request(url)
    req.get_method = lambda: get_method
    res = urlopen_with_retry(req)
    return res.geturl()


def urlopen_with_retry(*args, **kwargs):
    retry_time = 3
    for i in range(retry_time):
        # try:
        if insecure:
            # ignore ssl errors
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return request.urlopen(*args, context=ctx, **kwargs)
        else:
            return request.urlopen(*args, **kwargs)
        # except socket.timeout as e:
        #     logging.debug('request attempt %s timeout' % str(i + 1))
        #     if i + 1 == retry_time:
        #         raise e
        # # try to tackle youku CDN fails
        # except error.HTTPError as http_error:
        #     logging.debug('HTTP Error with code{}'.format(http_error.code))
        #     if i + 1 == retry_time:
        #         raise http_error


def get_content(url, headers={}, decoded=True):
    """Gets the content of a URL via sending a HTTP GET request.

    Args:
        url: A URL.
        headers: Request headers used by the client.
        decoded: Whether decode the response body using UTF-8 or the charset specified in Content-Type.

    Returns:
        The content as a string.
    """

    logging.debug('get_content: %s' % url)

    req = request.Request(url, headers=headers)
    if cookies:
        cookies.add_cookie_header(req)
        req.headers.update(req.unredirected_hdrs)

    response = urlopen_with_retry(req)
    data = response.read()

    # Handle HTTP compression for gzip and deflate (zlib)
    content_encoding = response.getheader('Content-Encoding')
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    # Decode the response body
    if decoded:
        charset = match1(
            response.getheader('Content-Type', ''), r'charset=([\w-]+)'
        )
        if charset is not None:
            data = data.decode(charset, 'ignore')
        else:
            data = data.decode('utf-8', 'ignore')

    return data




def url_size(url, faker=False, headers={}):
    if faker:
        response = urlopen_with_retry(
            request.Request(url, headers=fake_headers)
        )
    elif headers:
        response = urlopen_with_retry(request.Request(url, headers=headers))
    else:
        response = urlopen_with_retry(url)

    size = response.headers['content-length']
    return int(size) if size is not None else float('inf')


def urls_size(urls, faker=False, headers={}):
    return sum([url_size(url, faker=faker, headers=headers) for url in urls])




def url_info(url, faker=False, headers={}):
    logging.debug('url_info: %s' % url)

    if faker:
        response = urlopen_with_retry(
            request.Request(url, headers=fake_headers)
        )
    elif headers:
        response = urlopen_with_retry(request.Request(url, headers=headers))
    else:
        response = urlopen_with_retry(request.Request(url))

    headers = response.headers

    type = headers['content-type']
    if type == 'image/jpg; charset=UTF-8' or type == 'image/jpg':
        type = 'audio/mpeg'  # fix for netease
    mapping = {
        'video/3gpp': '3gp',
        'video/f4v': 'flv',
        'video/mp4': 'mp4',
        'video/MP2T': 'ts',
        'video/quicktime': 'mov',
        'video/webm': 'webm',
        'video/x-flv': 'flv',
        'video/x-ms-asf': 'asf',
        'audio/mp4': 'mp4',
        'audio/mpeg': 'mp3',
        'audio/wav': 'wav',
        'audio/x-wav': 'wav',
        'audio/wave': 'wav',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'application/pdf': 'pdf',
    }
    if type in mapping:
        ext = mapping[type]
    else:
        type = None
        if headers['content-disposition']:
            try:
                filename = parse.unquote(
                    r1(r'filename="?([^"]+)"?', headers['content-disposition'])
                )
                if len(filename.split('.')) > 1:
                    ext = filename.split('.')[-1]
                else:
                    ext = None
            except:
                ext = None
        else:
            ext = None

    if headers['transfer-encoding'] != 'chunked':
        size = headers['content-length'] and int(headers['content-length'])
    else:
        size = None

    return type, ext, size












def parse_host(host):
    """Parses host name and port number from a string.
    """
    if re.match(r'^(\d+)$', host) is not None:
        return ("0.0.0.0", int(host))
    if re.match(r'^(\w+)://', host) is None:
        host = "//" + host
    o = parse.urlparse(host)
    hostname = o.hostname or "0.0.0.0"
    port = o.port or 0
    return (hostname, port)


def set_proxy(proxy):
    proxy_handler = request.ProxyHandler({
        'http': '%s:%s' % proxy,
        'https': '%s:%s' % proxy,
    })
    opener = request.build_opener(proxy_handler)
    request.install_opener(opener)


def unset_proxy():
    proxy_handler = request.ProxyHandler({})
    opener = request.build_opener(proxy_handler)
    request.install_opener(opener)


# DEPRECATED in favor of set_proxy() and unset_proxy()
def set_http_proxy(proxy):
    if proxy is None:  # Use system default setting
        proxy_support = request.ProxyHandler()
    elif proxy == '':  # Don't use any proxy
        proxy_support = request.ProxyHandler({})
    else:  # Use proxy
        proxy_support = request.ProxyHandler(
            {'http': '%s' % proxy, 'https': '%s' % proxy}
        )
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)




def download_main(download, download_playlist, urls, playlist, **kwargs):
    for url in urls:
        if re.match(r'https?://', url) is None:
            url = 'http://' + url

        if playlist:
            download_playlist(url, **kwargs)
        else:
            download(url, **kwargs)











