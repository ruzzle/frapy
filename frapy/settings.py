# Scrapy settings for frapy project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'frapy'

SPIDER_MODULES = ['frapy.spiders']
NEWSPIDER_MODULE = 'frapy.spiders'

USER_AGENT = '%s1.0' % (BOT_NAME)

# NOTE: hier kan een verwerker voor sqlite in!
ITEM_PIPELINES = {
	#'frapy.pipelines.SqlitePipeline' : 1,
	#'frapy.pipelines.StdoutPipeline' : 2
	'frapy.pipelines.SqlAlchemyPipeline' : 2
}

#Sql alchemy database config
DATABASE = {
	'drivername' : 'sqlite',
	'username' : None,
	'password' : None,
	'host' : None,
	'port' : None,
	'database' : 'scraped/forums.db'
}