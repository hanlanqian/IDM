#!/usr/bin/env python
from .common import parse_host, set_proxy, unset_proxy


class Extractor():
    def __init__(self, *args):
        self.url = None
        self.title = None
        self.vid = None
        self.streams = {}
        self.streams_sorted = []

        if args:
            self.url = args[0]

class VideoExtractor():
    def __init__(self, *args):
        self.url = None
        self.title = None
        self.vid = None
        self.m3u8_url = None
        self.streams = {}
        self.streams_sorted = []
        self.audiolang = None
        self.password_protected = False
        self.dash_streams = {}
        self.caption_tracks = {}
        self.out = False
        self.ua = None
        self.referer = None
        self.danmaku = None
        self.lyrics = None
        self.real_urls = []

        if args:
            self.url = args[0]

    def download_by_url(self, url, **kwargs):
        self.url = url
        self.vid = None

        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            set_proxy(parse_host(kwargs['extractor_proxy']))
        self.prepare(**kwargs)

        if self.out:
            return
        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            unset_proxy()

        try:
            self.streams_sorted = [dict([('id', stream_type['id'])] + list(self.streams[stream_type['id']].items())) for stream_type in self.__class__.stream_types if stream_type['id'] in self.streams]
        except:
            self.streams_sorted = [dict([('itag', stream_type['itag'])] + list(self.streams[stream_type['itag']].items())) for stream_type in self.__class__.stream_types if stream_type['itag'] in self.streams]

        self.extract(**kwargs)

        self.download(**kwargs)

    def download_by_vid(self, vid, **kwargs):
        self.url = None
        self.vid = vid

        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            set_proxy(parse_host(kwargs['extractor_proxy']))
        self.prepare(**kwargs)
        if 'extractor_proxy' in kwargs and kwargs['extractor_proxy']:
            unset_proxy()

        try:
            self.streams_sorted = [dict([('id', stream_type['id'])] + list(self.streams[stream_type['id']].items())) for stream_type in self.__class__.stream_types if stream_type['id'] in self.streams]
        except:
            self.streams_sorted = [dict([('itag', stream_type['itag'])] + list(self.streams[stream_type['itag']].items())) for stream_type in self.__class__.stream_types if stream_type['itag'] in self.streams]

        self.extract(**kwargs)

        self.download(**kwargs)

    def prepare(self, **kwargs):
        pass
        #raise NotImplementedError()

    def extract(self, **kwargs):
        pass
        #raise NotImplementedError()






