# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from __future__ import unicode_literals

import sys
import re
import sqlite3
import inflect
import ipdb

from collections import defaultdict
from sqlalchemy.orm import sessionmaker, scoped_session

from scrapy import log #, signals
from scrapy.item import Field, Item
#from scrapy.xlib.pydispatch import dispatcher

from frapy.items import *
from frapy.models import *


class SqlAlchemyPipeline:
    
    #state = defaultdict(lambda: {})

    def open_spider(self, spider):
        engine = db_connect()
        create_table(engine)
        session_factory = sessionmaker(bind=engine)
        self.Session = scoped_session(session_factory)
        #dispatcher.connect(self.spider_opened, signals.spider_opened)

    #def spider_opened(self, spider):
    #    pass
        # Check whether we are resuming a session, else do nothing!
        # if spider.state:
        #     for user in spider.state['user_cache'].values():
        #         if not user._db_item: #Then it has not been processed yet, so do it anyways!
        #             user._db_item = DbUser(**user)
        #         user._db_item = self.Session().merge(user._db_item)
        #         self.Session.remove()

    def process_item(self, item, spider):
        clazz = eval('Db{0}'.format(item.__class__.__name__))
        db_item = clazz(**item)

        #NOTE: we assume that all items are processed sequentially (and atomic... i hope)
        for foreign_ref in item._refs.keys():
            foreign_item = item._refs[foreign_ref]
            if foreign_item:
                setattr(db_item, foreign_ref, foreign_item._db_item)

        try:
            db_session = self.Session()
            db_session.add(db_item)
            db_session.commit()
            item._db_item = db_item
        except Exception as e:
            ipdb.set_trace()
            print "message = %s" % e.message
            db_session.rollback()
        finally:
            self.Session.remove()
    
    def close_spider(self, spider):
        self.Session.close()
