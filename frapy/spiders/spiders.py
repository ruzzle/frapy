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

from abc import ABCMeta, abstractmethod
from urlparse import urlparse
from collections import defaultdict

from frapy.items import Post, User, Forum, Category, Thread
from frapy.conf import ConfigValidator, ConfigLoader
from util import *

from scrapy import log, signals
from scrapy.contrib.linkextractors import LinkExtractor
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

    def __init__(self, config=None, **kwargs):
        assert config, "Geen configuratie opgegeven"
        self.config = ConfigLoader.load(config, **kwargs)
        ConfigValidator.validate(self.config)

    def start_requests(self):
        #return [Request(self.config['url'], callback=self.parse_forum)]
        return []
    
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
        if conf.startswith('xpath:'):
            return LinkExtractor(restrict_xpaths=conf[6:]).extract_links(response)
        elif conf.startswith('regex:'):
            raise NotImplementedError("Regex link extractie nog niet geimplementeerd")
        else:
            raise NotImplementedError("Extractieprotocol niet geimplementeerd")

    def _extract_blocks(self, response, conf):
        if conf.startswith('xpath:'):
            return response.selector.xpath(conf[6:])
        elif conf.startswith('regex:'):
            raise NotImplementedError("Regex link extractie nog niet geimplementeerd")
        else:
            raise NotImplementedError("Extractieprotocol niet geimplementeerd")

    def _extract_attribute(self, inp, conf):
        if conf.startswith('xpath:'):
            selector = inp if isinstance(inp, Selector) else inp.selector
            return xpath2text(selector, conf[6:])
        else: #TOFIX
            raise NotImplementedError("Regex link extractie nog niet geimplementeerd")


    def parse_forum(self, response):
        """ Parses a forum main page"""

        log.msg("Parsing FORUM '{0}'".format(response.url), level=log.DEBUG)
        forum = Forum(domain=urlparse(response.url).hostname)
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

        #Check whether we are continuing an already parsed category
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
                                            forum=category._refs['forum']))

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

        #Check whether we are continuing an already parsed thread
        thread = response.meta.get('myself')
        if not thread: #Then it is the first time we encounter it, so extract :-)!
            attributes = self.config['thread']['attributes']
            thread = Thread(title=self._extract_attribute(response, attributes['title']),
                            url=response.url)
            thread._refs['category'] = response.meta.get('category')
            yield thread

        # Parse all posts/users on current thread
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

        # Extract possible next page of current thread and append to request buffer
        if self.config['thread'].get('next'):
            for next_page in self._extract_links(response, self.config['thread']['next']):  # which can only be 1
                yield Request(url=next_page.url,
                              callback=self.parse_thread,
                              meta=dict(myself=thread))

