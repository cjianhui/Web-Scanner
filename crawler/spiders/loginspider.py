from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

class LoginSpider(InitSpider):
    name = 'loginspider'
    allowed_domains = ['example.com']
    login_page = 'http://www.example.com/login'
    start_urls = ['http://www.example.com/useful_page/',
                  'http://www.example.com/another_useful_page/']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'-\w+.html$'),
             callback='parse_item', follow=True),
    )

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """Generate a login request."""
        return FormRequest.from_response(response,
                    formdata={'name': 'herman', 'password': 'password'},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if "Hi Herman" in response.body:
            self.log("Successfully logged in. Let's start crawling!")
            # Now the crawling can begin..
            return self.initialized()
        else:
            self.log("Bad times :(")
            # Something went wrong, we couldn't log in, so nothing happens.

    def parse(self, response):
		# scrape current URL
		item = URLItem()
		self.createURLItem(item, response.url)
		yield item 
		
		# scrape forms in current page, if it exists
		forms = response.css('form')
		for form in forms:
			formItem = FormItem()
			self.createFormItem(formItem, response.url, form)
			yield formItem
			
		# visit links in current page
		links = response.css('a::attr(href)').extract()
		for link in links:
			if link is not None:
				link = link.replace("///", "//", 1)
				link = response.urljoin(link)
				yield scrapy.Request(link, callback=self.parse)
		
		
			
	def createURLItem(self, item, url):
		parsed_url = urlparse(url)
		item['domain'] = parsed_url.netloc
		item['url'] = parsed_url.geturl()
		item['scheme'] = parsed_url.scheme
		item['path'] = parsed_url.path
		item['params'] = parsed_url.params
		item['query'] = parsed_url.query
		item['fragment'] = parsed_url.fragment
		item['port'] = parsed_url.port 
		
			
	def createFormItem(self, item, url, form):
		item['url'] = url
		parsed_url = urlparse(url)
		item['domain'] = parsed_url.netloc
		item['scheme'] = parsed_url.scheme
		item['path'] = parsed_url.path
		item['query'] = parsed_url.query
		form_id = form.css('::attr(id)').extract_first()
		
		if form_id is None:
			form_id = ''
		item['form_id'] = form_id
		
		form_action = form.css('::attr(formaction)').extract_first()
		if form_action is None:
			form_action = ''
		item['action'] = form_action
			
		form_method = form.css('::attr(method)').extract_first()
		if form_method is None:
			form_method = ''
		item['method'] = form_action
		
		inputs = form.css('input')
		item['inputs'] = []
		for input in inputs:
			input_dict = {}
			input_type = input.css('::attr(type)').extract_first()
			if input_type is None:
				input_type = ''
			input_dict['type'] = input_type
			input_name = input.css('::attr(name)').extract_first()
			if input_name is None:
				input_name = ''
			input_dict['name'] = input_name
			input_value = input.css('::attr(value)').extract_first()
			if input_value is None:
				input_value = ''
			input_dict['value'] = input_value
			item['inputs'].append(input_dict)

