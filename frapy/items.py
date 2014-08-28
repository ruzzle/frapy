# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from __future__ import unicode_literals
from scrapy.item import Item, Field

class FrapyItem(Item):
    _refs = None
    _db_item = None

    def __init__(self, *args, **kwargs):
        super(FrapyItem, self).__init__(*args, **kwargs)
        self._refs = {}

class Forum(FrapyItem):
    domain = Field()  # R
    
    def __str__(self):
        return str('Forum { domain : %s }' % self['domain']).encode('utf8')

class Category(FrapyItem):
    title = Field()  # R
    url = Field() # R (automatic)

    def ancestors(self):
        if self._refs['parent']:
            self._refs['parent'].ancestors()
            yield self._refs['parent']

    def __str__(self):
        chain = " -> ".join(a['title'] for a in list(self.ancestors()) + [self])
        return u'Category "{0}"'.format(chain).encode('utf-8')

class Thread(FrapyItem):
    title = Field()  # R
    url = Field() # R (automatic)

class Post(FrapyItem):
    content = Field()  # R [NOTE: we assume that forums don't allow multiple users to register the same nickname]
    timestamp = Field(serializer=str)  # R
    
class User(FrapyItem):
    nickname = Field() #R
    name = Field()
    join_date = Field(serializer=str)
    location = Field()
