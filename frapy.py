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
    #try:
        cmd = 'scrapy crawl -L INFO -a config=qnap generic -s JOBDIR=crawls/generic-1'
        execute(cmd.split())
    #except Exception as e:
    #    print e.message
    

def test():
    try:
        os.unlink("scraped/forums.db")
    except OSError:
        pass
    
    #cmd = 'scrapy crawl -L INFO -a config=phpbb3 -a url=http://www.raspberrypi.org/phpBB3 generic'
    #cmd = 'scrapy crawl -L INFO -a config=phpbb3.0.x generic -s JOBDIR=crawls/generic-1'
    #cmd = 'scrapy crawl -L INFO -a config=phpbb3.0.x generic'
    #cmd = 'scrapy crawl -L DEBUG -a config=phpbb3.0.x.test generic'
    cmd = 'scrapy crawl -L INFO -a config=qnap generic'
    execute(cmd.split())




if __name__ == '__main__':
    #test()
    main()
 