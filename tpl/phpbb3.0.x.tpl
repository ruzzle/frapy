# This is an example configuration file for a forum to parse

#Defines scraping configuration of a webforum. Should include start_url with forum main page
forum: {
	category: { xpath: '//div[@class="container"]//h2' }
}

#Defines scraping configuration of forum categories
category: {
	attributes: {
		title: { xpath: '//div[@class="container"]//h2/a' }
	}
	subcategory: { xpath: '//a[@class="forumtitle"]' }
	thread: { xpath: '//a[@class="topictitle"]' }
	next: { xpath: '//fieldset[@class="display-options"]/a[contains(., "Next")]' }
}

#Defines scraping configuration of forum threads
thread: {
	attributes: {
		title: { xpath: '//div[@class="container"]//h2' }
		timestamp: { xpath: '(//div[@class="author"])[1]/text()[2]' }
	}
	next: { xpath: '(//div[contains(@class,"paging")])[1]/span/strong/following-sibling::a[1]' }
	post: { xpath: '//div[@class="postbody"]/../..' }
}

#(//div[contains(@class,"paging")])[1]/span/strong/following-sibling::a[1]

#Defines scraping configuration of forum posts
post: {
	attributes: {
		post_content: { xpath: './/div[@class="postbody"]/../..' }
		post_timestamp: { xpath: './/p[@class="author"]/text()[2]' }
		user_nickname: { xpath: './/p[@class="author"]//strong' }
		user_location: { xpath: './/strong[text()[contains(., "Location")]]/following-sibling::text()' }
		user_join_date: { xpath: './/strong[text()[contains(., "Joined")]]/following-sibling::text()' }
	},
}