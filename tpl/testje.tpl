# This is an example configuration file for a forum to parse

base: 'phpbb3.0.x.test'

#Defines scraping configuration of a webforum
forum: {
	category: { xpath: '//a[@class="forumtitle"]' }
}

#Defines scraping configuration of forum categories
category: {
	attributes: {
		title: { xpath: '//h2/a[contains(@href, "viewforum")][1]' }
	}
	subcategory: { xpath: '//a[@class="forumtitle"]' }
	thread: { xpath: '//a[@class="topictitle"]' }
	next: { xpath: '//fieldset[@class="display-options"]/a[contains(., "Next")]' }
}

#Defines scraping configuration of forum threads
thread: {
	attributes: {
		title: { xpath: '//h2[1]' }
	}
	next: { xpath: '(//span[@class="page-sep"]/preceding-sibling::strong/following-sibling::a[1])[1]' }
	post: { xpath: '//div[contains(concat(" ",@class," ")," post ")]' } #concat trick
}

#Defines scraping configuration of forum posts
post: {
	attributes: {
		post_content: { xpath: './/div[@class="postbody"]/../..' }
		post_timestamp: { xpath: './/p[@class="author"]/text()[2]' }
		user_nickname: { xpath: './/p[@class="author"]//strong' }
		user_location: { xpath: './/strong[text()[contains(., "Location")]]/following-sibling::text()' }
		user_join_date: { xpath: './/strong[text()[contains(., "Joined")]]/following-sibling::text()' }
	}
}

#TODO USERS
