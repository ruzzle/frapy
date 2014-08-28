#!/usr/bin/env python

import os
from config import Config
from scrapy.cmdline import execute

'''

Cmd usage:
> scrapy runspider frapy/spiders/__init__.py -a url=http://forum.qnap.com

'''
# TODO: give arguments to frapy!
def main():
    
    #try:
    #    os.unlink("scraped/forums.db")
    #except OSError:
    #    pass
    
    #config = Config(file('example.cfg'))
    #print config
    # Start scrapy with some arguments!
    cmd = 'scrapy crawl -L INFO -a template=phpbb3.0.x.test -a url=http://forum.qnap.com generic -s JOBDIR=crawls/generic-1'
    execute(cmd.split())
    

def test():
    try:
        os.unlink("scraped/forums.db")
    except OSError:
        pass
    
    #cmd = 'scrapy crawl -L INFO -a template=phpbb3 -a url=http://www.raspberrypi.org/phpBB3 generic'
    #cmd = 'scrapy crawl -L INFO -a template=phpbb3.0.x -a url=http://forum.qnap.com generic -s JOBDIR=crawls/generic-1'
    #cmd = 'scrapy crawl -L INFO -a template=phpbb3.0.x -a url=http://forum.qnap.com generic'
    #cmd = 'scrapy crawl -L DEBUG -a template=phpbb3.0.x.test -a url=http://forum.qnap.com generic'
    cmd = 'scrapy crawl -L INFO -a template=phpbb3.0.x.test -a url=http://forum.qnap.com generic'
    execute(cmd.split())




if __name__ == '__main__':
    #test()
    main()
 