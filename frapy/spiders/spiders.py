'''
Created on 10 jan. 2013

@author: marinus

    NOTES:
    - scannen per thread, dan db management?
    
    TODO:
    - inlog geneuzel
    - cookie-law geneuzel >.<
    - resume functie
    - check newest post functie
    - robots.txt ;-)

'''

import re
import os.path
from abc import ABCMeta, abstractmethod
from urlparse import urlparse
from collections import defaultdict
from config import Config

from frapy.items import Post, User, Forum, Category, Thread
from util import *

from scrapy import log, signals
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.xlib.pydispatch import dispatcher

#DEBUG
import ipdb

'''
This is a base class for every spider used in frapy
If you want to create a new spider, extend this one! 
'''
class BaseForumSpider(Spider):
    
    __metaclass__ = ABCMeta
    
    name = 'base'

    def __init__(self, template=None, url=None):
        assert url, "Geen geldige start url opgegeven"
        assert template, "Geen configuratie bestand opgegeven"
        self.config = self._load_config(template)
        self.url = url
    
    def _load_config(self, template):
        template_path = "tpl/{0}.tpl".format(template)
        assert os.path.isfile(template_path), "Configuratie bestand '{0}' niet aanwezig".format(template_path)
        config = dict(Config(template_path))
        if config.has_key('base'):
            return _load_config(config['base']).update(config)
        else:
            return config


    def start_requests(self):
        return [Request(self.url, callback=self.parse_forum), Request(self.url, callback=self.parse_forum)]
    
    @abstractmethod
    def parse_forum(self, response):
        pass
    

'''
A Generic spider which parses by forum configuration
'''
class GenericForumSpider(BaseForumSpider):

    name = 'generic'
    state = None

    def __init__(self, *args, **kwargs):
        super(GenericForumSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self._after_open, signals.spider_opened)

    def _after_open(self):
        if not self.state:
            self.state = defaultdict(dict)

    def _extract_links(self, response, conf):
        assert conf.get('xpath') or conf.get('regex'), "Type extractie is geen 'regex' of 'xpath'"
        if conf.get('xpath'):
            return SgmlLinkExtractor(restrict_xpaths=conf['xpath']).extract_links(response)
        else:
            raise NotImplementedError("Regex link extractie nog niet geimplementeerd")

    def _extract_blocks(self, response, conf):
        assert conf.get('xpath') or conf.get('regex'), "Type extractie is geen 'regex' of 'xpath'"
        if conf.get('xpath'):
            return Selector(response).xpath(conf['xpath'])
        else: #TOFIX
            raise NotImplementedError("Regex link extractie nog niet geimplementeerd")

    def _extract_attribute(self, inp, conf):
        assert conf.get('xpath') or conf.get('regex'), "Type extractie is geen 'regex' of 'xpath'"
        assert isinstance(inp, Response) or isinstance(inp, Selector), "Onbekende input gegeven bij attribuut extractie"
        if conf.get('xpath'):
            selector = inp if isinstance(inp, Selector) else Selector(inp)
            return xpath2text(selector, conf['xpath'])
        else: #TOFIX
            raise NotImplementedError("Regex link extractie nog niet geimplementeerd")


    def parse_forum(self, response):
        """ Parses a forum main page"""

        #if not self.state:

        log.msg("Parsing FORUM '{0}'".format(response.url), level=log.DEBUG)
        forum = Forum(domain=urlparse(self.url).hostname)
        yield forum
        
        categories = self._extract_links(response, self.config['forum']['category'])
        if categories:
            log.msg("Extracted %d categories from forum" % len(categories), level=log.INFO)
            for category in categories:
                yield Request(url=category.url,
                              callback=self.parse_category,
                              meta=dict(forum=forum))

    def parse_category(self, response):
        """ Parses a forum category page """
        log.msg("Parsing CATEGORY '{0}'".format(response.url), level=log.DEBUG)

        #If not previously extracted, extract category
        category = response.meta.get('myself')
        if not category: #Then it is the first time we encounter it, so extract :-)!
            attributes = self.config['category']['attributes']
            category = Category(title=self._extract_attribute(response, attributes['title']),
                                url=response.url)
            category._refs['parent'] = response.meta.get('parent')
            category._refs['forum'] = response.meta.get('forum')
            yield category
        
        #Find any subcategories that may be present, and recurse into same function
        if self.config['category'].get('subcategory'):
            subcategories = self._extract_links(response, self.config['category']['subcategory'])
            if subcategories:
                log.msg("Extracted %d subcategories from category" % len(subcategories), level=log.INFO)
                for subcategory in subcategories:
                    yield Request(url=subcategory.url,
                                  callback=self.parse_category,
                                  meta=dict(parent=category,
                                            forum=category.get('forum_ref')))

        # Extract all threads present on current category page
        threads = self._extract_links(response, self.config['category']['thread'])
        if threads:
            log.msg("Extracted %d threads from category '%s'" % (len(threads), category['title']), level=log.INFO)
            for thread in threads:
                yield Request(url=thread.url,
                              callback=self.parse_thread,
                              meta=dict(category=category))
        
        # Extract possible next page of current category and append to request buffer
        if self.config['category'].get('next'):
            for next_page in self._extract_links(response, self.config['category']['next']):
                yield Request(url=next_page.url,
                              callback=self.parse_category,
                              meta=dict(myself=category))
    

    def parse_thread(self, response):
        """ Parses a forum thread page"""

        log.msg("Parsing THREAD '{0}'".format(response.url), level=log.DEBUG)

        #ipdb.set_trace()
        thread = response.meta.get('myself')
        if not thread: #Then it is the first time we encounter it, so extract :-)!
            attributes = self.config['thread']['attributes']
            thread = Thread(title=self._extract_attribute(response, attributes['title']),
                            url=response.url)
            thread._refs['category'] = response.meta.get('category')
            yield thread

        # Parse all posts/users on thread page and add items to item buffer
        #ipdb.set_trace()
        #ipdb.set_trace = self._after_open

        posts = self._extract_blocks(response, self.config['thread']['post'])
        if posts:
            log.msg("Extracted %d posts from thread '%s'" % (len(posts), thread['title']), level=log.INFO)
            for p in posts:
                attributes = self.config['post']['attributes']
                post_content = self._extract_attribute(p, attributes['post_content'])
                post_timestamp = text2date(self._extract_attribute(p, attributes['post_timestamp']))
                user_nickname = self._extract_attribute(p, attributes['user_nickname'])
                user_location = self._extract_attribute(p, attributes['user_location'])
                user_join_date = text2date(self._extract_attribute(p, attributes['user_join_date']))

                user = self.state['user_cache'].get(user_nickname)
                if not user:
                    user = self.state['user_cache'][user_nickname] = \
                        User(nickname=user_nickname,
                             join_date=user_join_date,
                             location=user_location)
                    user._refs['forum'] = thread._refs['category']._refs['forum']
                    yield user

                post = Post(content=post_content,
                            timestamp=post_timestamp)
                post._refs['thread'] = thread
                post._refs['user'] = user
                yield post

            #if user_nickname == 'saiello':
            #    ipdb.set_trace()
            #print '%s | %s | %s' % (thread['title'], user['nickname'], str(post_timestamp))
            
            #yield post
        
        # Extract possible next page of current thread and append to request buffer
        if self.config['thread'].get('next'):
            for next_page in self._extract_links(response, self.config['thread']['next']):  # which can only be 1
                yield Request(url=next_page.url,
                              callback=self.parse_thread,
                              meta=dict(myself=thread))

