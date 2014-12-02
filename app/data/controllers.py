#Flask dependencies
from flask import Blueprint, request
from urllib import urlopen

import json
from app.data.models import JNYTDocument
import shares, utils, time
from bs4 import BeautifulSoup
from datetime import datetime
from mongoengine import NotUniqueError

from app.data.PoliticalBias import politicalLeaning

# Define the blueprint: 'data', set its url prefix: app.url/data
mod_data = Blueprint('data', __name__, url_prefix='/data')

@mod_data.route('/')
def index():
	return utils.get_nyt_article_search_url("US+Presidential+Election&begin_date=20120101&end_date=20121231")

##Conservative Blogs

#http://wizbangblog.com/category/2012-presidential-race/
@mod_data.route('/conservative/parse-wizbang')
def parse_wizbang():
	base_url_2012 = "http://wizbangblog.com/category/2012-presidential-race/" #upto 23
	base_url_2008 = "http://wizbangblog.com/category/2008-presidential-race/" #upto 51

	for page_num in range(1, 24):
		if page_num > 1:
			url = base_url_2012 + 'page/' + `page_num`
		else:
			url = base_url_2012

		parseWizBangUrl(url)
		#break

	for page_num in range(1, 52):
		if page_num > 1:
			url = base_url_2008 + 'page/' + `page_num`
		else:
			url = base_url_2008

		parseWizBangUrl(url)
		#break

	return `page_num`

def parseWizBangUrl(url):
	browser_data = utils.getDataAsABrowserRequest(url)
	if browser_data.status_code == 200:
		soup = BeautifulSoup(browser_data.text).find("div",{"id":"content_box"})

		articles = soup.findAll("article")

		for article in articles:
			title_link = article.find("header").find("a")
			date_string = article.find("header").find("span",{"class":"thetime updated"}).get_text()

			wizbangblogDoc = JNYTDocument()
			wizbangblogDoc.web_url = title_link['href']
			wizbangblogDoc.political_leaning = "Conservative"
			wizbangblogDoc.source = "WizBang Blog"
			wizbangblogDoc.headline = title_link.get_text().strip()
			wizbangblogDoc.pub_date = datetime.strptime(date_string.strip(),"%B %d, %Y")
			wizbangblogDoc.save()

			#Getting the social shares for the URL
			#wizbangblogDoc.social_shares = shares.get_social_counts(wizbangblogDoc.web_url)
			#wizbangblogDoc.save()

			browser_request = utils.getDataAsABrowserRequest(wizbangblogDoc.web_url)
			if browser_request.status_code == 200:
				content_soup = BeautifulSoup(browser_request.text).find("div",{"class":"thecontent"}).findAll("p")
				article_content = ""
				text = ""

				for paragraph in content_soup:
					text = paragraph.get_text()
					article_content += " "+ text

				wizbangblogDoc.content = article_content.strip()
				wizbangblogDoc.save()

@mod_data.route('/conservative/parse-redstate')
def parse_redstate():
	base_url = "http://www.redstate.com/search/presidential+elections+2012/page/"
	
	for page_num in range(1,63):
		url = base_url + `page_num`
		soup = BeautifulSoup(utils.getData(url))

		articles = soup.find("ul",{"class":"story-loop"}).findAll("ul",{"class","post"})

		for index, article in enumerate(articles):
			title_link = article.find("a")
			date_string = article.find("span",{"class":"byline-italic"})
			date_string = date_string.get_text().split(" at ")[0]
			date_string = date_string.replace("th,",",")
			date_string = date_string.replace("st,",",")
			date_string = date_string.replace("nd,",",")
			date_string = date_string.replace("rd,",",")

			redStateDoc = JNYTDocument()
			redStateDoc.web_url = title_link['href']
			redStateDoc.political_leaning = "Conservative"
			redStateDoc.source = "RedState"
			redStateDoc.headline = title_link.get_text().strip()
			redStateDoc.pub_date = datetime.strptime(date_string.strip(),"%B %d, %Y")
			redStateDoc.save()

			#Getting the social shares for the URL
			#redStateDoc.social_shares = shares.get_social_counts(redStateDoc.web_url)
			#redStateDoc.save()

			content_soup = BeautifulSoup(utils.getData(redStateDoc.web_url)).find("div",{"class":"the-content"}).findAll("p")
			article_content = ""
			text = ""

			for paragraph in content_soup:
				text = paragraph.get_text()
				article_content += " "+ text

			article_content = article_content.replace(text,"")

			redStateDoc.content = article_content.strip()
			redStateDoc.save()

		# break

	return `page_num`

@mod_data.route('/conservative/parse-pjmedia')
def parse_pj_media():
	# JNYTDocument.drop_collection()
	#http://pjmedia.com/page/1/?s=presidential+elections+2012&submit_x=0&submit_y=0&search_sortby=date
	base_url = "http://pjmedia.com/page/<<page_num>>/?s=presidential+elections+2012&submit_x=0&submit_y=0&search_sortby=date"
	page_num = 1

	while True:
		url = base_url.replace("<<page_num>>",`page_num`)
		html_content = utils.getData(url)

		if html_content == None:
			break
		
		soup = BeautifulSoup(html_content)
		articles = soup.find("div",{"id":"archive-content"}).findAll("div",{"class":"category-story"})

		for article in articles:
			pjMediaDoc = JNYTDocument()
			link = article.find("h2").find("a")
			meta_data = [string.strip() for string in article.find("div",{"class":"category-author2"}).get_text().split('-')]

			date_str = meta_data[0]
			date_str = date_str.replace("th,",",")
			date_str = date_str.replace("st,",",")
			date_str = date_str.replace("nd,",",")
			date_str = date_str.replace("rd,",",")

			pjMediaDoc.web_url = link['href']
			pjMediaDoc.political_leaning = "Conservative"
			pjMediaDoc.source = "PJ Media"
			pjMediaDoc.headline = link.get_text().strip()
			pjMediaDoc.pub_date = datetime.strptime(date_str,"%A, %B %d, %Y")
			pjMediaDoc.save()

			#Getting the social shares for the URL
			#pjMediaDoc.social_shares = shares.get_social_counts(pjMediaDoc.web_url)
			#pjMediaDoc.save()

			#Getting the content of the document
			content_soup = BeautifulSoup(utils.getData(pjMediaDoc.web_url+"?singlepage=true")).find("div",{"class":"post"}).find("div",{"class":"clearingfix"}).findAll("p")
			article_content = ""

			for paragraph in content_soup:
				text = paragraph.get_text()
				article_content += " "+ text

			pjMediaDoc.content = article_content.strip()
			pjMediaDoc.save()

		page_num += 1

	return `page_num`

@mod_data.route('/conservative/parse-michelle-malkin')
def parse_michelle_malkin():
	#JNYTDocument.drop_collection()
	#http://michellemalkin.com/page/1/?s=presidential+elections+2012

	base_url = "http://michellemalkin.com/page/<<page_num>>/?s=presidential+elections+2012"
	page_num = 1

	while True:
		url = base_url.replace("<<page_num>>", `page_num`)
		soup = BeautifulSoup(utils.getData(url)).find("div",{"id":"content"})

		title = soup.find("h1",{"class":"leadStoryAlt"})

		if title == "Not Found":
			break

		article = soup.find("div",{"class":"article"})

		headings = article.findAll("h2")
		author = article.findAll("div",{"class":"author"})

		for index, h2 in enumerate(headings):
			link = h2.find("a")
			meta_data = [string.strip() for string in author[index].get_text().encode('utf-8').split('\xc2\xa0\xc2\xa0')]
			
			michelleMalkinDoc = JNYTDocument()

			michelleMalkinDoc.web_url = link['href']
			michelleMalkinDoc.political_leaning = "Conservative"
			michelleMalkinDoc.source = "Michelle Malkin"
			michelleMalkinDoc.headline = link.get_text()
			michelleMalkinDoc.pub_date = datetime.strptime(meta_data[2],"%B %d, %Y %I:%M %p")
			michelleMalkinDoc.save()

			#Getting the social shares for the URL
			#michelleMalkinDoc.social_shares = shares.get_social_counts(michelleMalkinDoc.web_url)
			#michelleMalkinDoc.save()

			#Getting the document content.
			content_soup = BeautifulSoup(utils.getData(michelleMalkinDoc.web_url)).find("div",{"class":"blog"}).findAll("p")
			article_content = ""

			for paragraph in content_soup:
				text = paragraph.get_text()
				if text.startswith("**Written by ") or text.startswith("Twitter @"):
					continue
				article_content += " "+ text
			
			michelleMalkinDoc.content = article_content.strip()
			michelleMalkinDoc.save()

		page_num += 1
	return `index`


##Liberal blogs

@mod_data.route('/liberal/parse-crooksnliars')
def parse_crooksnliars():
	#JNYTDocument.drop_collection()
	base_url = "http://crooksandliars.com/solr/presidential%20elections%202012?page=<<page_num>>&filters=im_cl_section%3A1"
	page_num = 0

	while page_num < 313:
		url = base_url.replace("<<page_num>>", `page_num`)
		url_content = utils.getData(url)
		soup = BeautifulSoup(url_content).find("div",{"class":"search-results"})

		content_nodes = soup.findAll("div",{"class":"buildmode-teaser"})

		for index, div in enumerate(content_nodes):
			crooksNLiarsDoc = JNYTDocument()
			title = div.find("div",{"class","field-title"}).find("a")

			field_submitted = div.find("div",{"class":"field field-submitted submitted"})
			author_link = field_submitted.find("a")

			temp_string = field_submitted.get_text()
			temp_string = temp_string.replace("By","")
			

			temp_string = temp_string.replace(author_link.get_text(),"").strip()
			date_string = temp_string.split("-")[0].strip().rsplit(" ",2)[0]
			date_string = date_string.replace("Anonymous","")
			
			crooksNLiarsDoc.web_url = "http://crooksandliars.com" + title["href"]
			crooksNLiarsDoc.headline = title.get_text().strip()
			crooksNLiarsDoc.political_leaning = "Liberal"
			crooksNLiarsDoc.source = "Crooks N Liars"
			crooksNLiarsDoc.pub_date = datetime.strptime(date_string.strip(),"%B %d, %Y")
			crooksNLiarsDoc.save()

			#Getting the social shares for the URL
			#crooksNLiarsDoc.social_shares = shares.get_social_counts(crooksNLiarsDoc.web_url)
			#crooksNLiarsDoc.save()

			try:
				content_soup = BeautifulSoup(utils.getData(crooksNLiarsDoc.web_url)).find("div",{"class":"nd-region-middle-wrapper"})
				crooksNLiarsDoc.content = content_soup.get_text()
				crooksNLiarsDoc.save()
			except:
				pass
			# break
		# break
		page_num = page_num + 1
	return `page_num`
			


@mod_data.route('/liberal/parse-talkingpointsmemo')
def parse_talkingpointsmemo():
	#JNYTDocument.drop_collection()
	base_url = "https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=10&hl=en&prettyPrint=false&source=gcsc&gss=.com&sig=23952f7483f1bca4119a89c020d13def&start=<<start_num>>&cx=partner-pub-7451232131633930:5915231553&q=presidential%20elections%202012&safe=active&googlehost=www.google.com&callback=google.search.Search.apiary272&nocache=1416895033146"
	start_num = 10
	
	while start_num < 100:
		# if start_num == 30:
		# 	break

		url = base_url.replace("<<start_num>>", `start_num`)
		url_content = utils.getData(url)

		url_content = url_content.replace("// API callback","")
		url_content = url_content.replace("google.search.Search.apiary272(","").strip()
		url_content = url_content[:-2]

		data = json.loads(url_content)
		for result in data["results"]:
			# print result["titleNoFormatting"], result["url"]

			talkingPointsMemoDoc = JNYTDocument()
			talkingPointsMemoDoc.web_url = result["url"]
			talkingPointsMemoDoc.headline = result["titleNoFormatting"]
			talkingPointsMemoDoc.political_leaning = "Liberal"
			talkingPointsMemoDoc.source = "Talking Points Memo"
			talkingPointsMemoDoc.save()

			#Getting the social shares for the URL
			talkingPointsMemoDoc.social_shares = shares.get_social_counts(talkingPointsMemoDoc.web_url)
			talkingPointsMemoDoc.save()

			try:
				content_soup = BeautifulSoup(utils.getData(talkingPointsMemoDoc.web_url))
				by_line = content_soup.find("section",{"class":"byline"}).find("time")

				date_string = by_line.get_text().strip().rsplit(",",1)[0]
				
				talkingPointsMemoDoc.pub_date = datetime.strptime(date_string.strip(),"%B %d, %Y")
				content = content_soup.find("div",{"class":"story-teaser"})
				body_content = content_soup.find("div",{"class":"story-body"})

				main_content = content.get_text() + " " + body_content.get_text()
				talkingPointsMemoDoc.content = main_content.strip()
				talkingPointsMemoDoc.save()
			except:
				print "Exception occured"
				pass

		start_num += 10
		# break
	return 'Anand'


@mod_data.route('/liberal/parse-fivethirtyeight')
def parse_fivethirtyeight():
	#JNYTDocument.drop_collection()

	base_url = "http://fivethirtyeight.com/page/<<page_num>>/?s=presidential+elections+2012"
	page_num = 1

	while True:
		url = base_url.replace("<<page_num>>", `page_num`)
		url_content = utils.getData(url)

		if url_content is None:
			break

		# if page_num == 3:
		# 	break
		
		# soup = BeautifulSoup(utils.getData(url))
		# print soup
		soup = BeautifulSoup(url_content).find("div",{"id":"main"})
		posts = soup.findAll("div")

		for index, div in enumerate(posts):
			if index == 0:
				continue
			#do something with the individual posts here..
			date_string = div.find("span",{"class":"datetime updated"}).get_text()
			link = div.find("h2",{"class":"article-title entry-title"}).find("a")

			fivethirtyeightDoc = JNYTDocument()

			fivethirtyeightDoc.web_url = link['href'].strip()
			fivethirtyeightDoc.political_leaning = "Liberal"
			fivethirtyeightDoc.source = "FiveThirtyEight"
			fivethirtyeightDoc.headline = link.get_text().strip()
			fivethirtyeightDoc.pub_date = datetime.strptime(date_string.strip(),"%b %d, %Y")
			fivethirtyeightDoc.save()

			#Getting the social shares for the URL
			#fivethirtyeightDoc.social_shares = shares.get_social_counts(fivethirtyeightDoc.web_url)
			#fivethirtyeightDoc.save()

			try:
				content_soup = BeautifulSoup(utils.getData(fivethirtyeightDoc.web_url)).find("div",{"class":"entry-content"})
				fivethirtyeightDoc.content = content_soup.get_text()
				fivethirtyeightDoc.save()
			except:
				pass
			#print date_string.strip(), title_link.get_text().strip(), title_link['href'].strip()
			# break
		# break
		page_num = page_num + 1
	return `index`
	

@mod_data.route('/liberal/parse-dailykos')
def parse_dailykos():
	#JNYTDocument.drop_collection()
	
	#URL for a search for the term US Presidential elections between 05/01/2011 and 05/31/2013
	base_url = "http://www.dailykos.com/search?submit=Search&time_begin=05%2F01%2F2011&text_type=any&search_type=search_stories&order_by=-time&text_expand=contains&text=US%20Presidential%20Elections&time_type=time_published&usernames=%28usernames%29&tags=%28tags%29&time_end=05%2F31%2F2013&page="

	main_url = base_url+"1"
	main_soup = BeautifulSoup(utils.getData(main_url)).find("div",{"class":"ajax-form-results ajax-delay-load"})

	no_of_items = main_soup.find("h4",{"class":"sub-head"}).get_text()
	no_of_items = no_of_items.replace(" results were found","")
	no_of_items = int(no_of_items)

	no_of_pages = no_of_items / 50

	#They rate limit the requests coming in from an bot. So an initial wait period before the loop begins..
	#Inside the loop, parsing the other contents would introduce the sufficient wait time. 
	time.sleep(10)

	for page_num in range(1, 30):
		url = base_url + `page_num`
		soup = BeautifulSoup(utils.getData(url)).find("div",{"class":"ajax-form-results ajax-delay-load"})

		table_list = soup.find("table",{"class":"styled storiesAsGrid"})

		if table_list != None:
			tbody = table_list.find("tbody")
			if tbody != None:
				link_rows = tbody.findAll("tr")
				for link_row in link_rows:
					dailyKosDoc = JNYTDocument()
					link = link_row.find("td",{"class":"first"}).find("a",{"class":"title"})
					date = link_row.find("td",{"class":"sm date"})

					dailyKosDoc.pub_date = datetime.strptime(date.get_text(),'%m/%d/%Y')
					dailyKosDoc.source = "DailyKos"
					dailyKosDoc.web_url = "http://www.dailykos.com" + link['href']
					dailyKosDoc.headline = link.get_text()
					dailyKosDoc.political_leaning = "Liberal"
					dailyKosDoc.save()

					#Getting the social shares for the URL
					#dailyKosDoc.social_shares = shares.get_social_counts(dailyKosDoc.web_url)
					#dailyKosDoc.save()
					
					#Getting the content of the URL
					try:
						content_soup = BeautifulSoup(utils.getData(dailyKosDoc.web_url)).find("div",{"id":"storyWrapper"}).find("div",{"class":"article-body"})
						dailyKosDoc.content = content_soup.get_text()
						dailyKosDoc.save()
					except:
						pass
					#break
		#if page_num == 2:
		#	break
	return `page_num`


@mod_data.route('/parse-time')
def parse_time():
	current_page_url = "http://search.time.com/results.html?Ntt=us+presidential+elections&Nf=p_date_range%7cBTWN+20110101+20130531"

	while current_page_url != None:
		soup = BeautifulSoup(utils.getData(current_page_url)).find("div",{"class":"resultsCol"})

		pagination = soup.find("div",{"class":"pagi"}).find("a",{"title":"Next"})
		if pagination != None:
			current_page_url = pagination["href"]
		else:
			current_page_url = None
		
		articles = soup.findAll("div",{"class":"tout"})

		for article in articles:
			image_div = article.find("div",{"class":"img"})
			if image_div != None:
				title_link = article.find("h3").find("a")
				date_string = article.find("span",{"class":"date"}).get_text().strip()
				
				content_soup = BeautifulSoup(utils.getData(title_link['href'])).find("div",{"class":"entry-content"})

				if content_soup != None:
					content_soup = content_soup.findAll("p")

					article_content = ""
					for p in content_soup:
						article_content += p.get_text().strip()
					print title_link['href'], title_link.get_text(), date_string

					timeDoc = JNYTDocument()
					timeDoc.pub_date = datetime.strptime(date_string,'%b %d, %Y')
					timeDoc.source = "Time"
					timeDoc.web_url = title_link['href']
					timeDoc.headline = title_link.get_text()
					timeDoc.content = article_content
					timeDoc.save()

				#Getting the social shares for the URL
				#timeDoc.social_shares = shares.get_social_counts(timeDoc.web_url)
				#timeDoc.save()
		#current_page_url = None
	return current_page_url

def get_nyt_data(url):
	browser_request = utils.getDataAsABrowserRequest(url)
	sent = ""
	if browser_request.status_code == 200:
		soup1 = BeautifulSoup(browser_request.text)

		soup = soup1.findAll("p",{"itemprop": "articleBody"})
		if soup == None or len(soup) == 0:
			soup = soup1.find("div", {"id": "articleBody"})
			if soup!=None:
				soup = soup.findAll("p")
		if soup == None or len(soup)==0:
			soup = soup1.find("div", {"class": "articleBody"}) 
			if soup!=None:
				soup = soup.findAll("p")
		if soup!=None and len(soup)>0:
			if type(soup) is not str:
				sent = " ".join([word.get_text() for word in soup])
				sent = sent.replace("\n","")
				sent = sent.strip()
			else:
				sent = soup
	return sent

@mod_data.route('/parse-nyt')
def parse_nyt():
	#JNYTDocument.drop_collection()
	params = 'US+Presidential+Election&begin_date=20120101&end_date=20121231&fq=source:("The New York Times")'
	base_url = utils.get_nyt_article_search_url(params)

	# 0 - 16
	# for page_num in range(39, 101):
	for page_num in range(1, 16):
		url = base_url + "&page=" + `page_num`
		response = urlopen(url).read()
		response = json.loads(response)

		print "Parsing: " + `page_num`

		for article in response["response"]["docs"]:
			try:
				nytimesDoc = JNYTDocument()
				nytimesDoc.web_url = article["web_url"]
				nytimesDoc.save()
				nytimesDoc.source = article["source"]
				nytimesDoc.pub_date = datetime.strptime(article["pub_date"],'%Y-%m-%dT%H:%M:%SZ')
				nytimesDoc.headline = article["headline"]['main']
				# nytimesDoc.snippet = article["snippet"]
				# nytimesDoc.lead_paragraph = article["lead_paragraph"]
				# nytimesDoc.abstract = article["abstract"]
				#nytimesDoc.print_page = article["print_page"]
				# nytimesDoc.document_type = article["document_type"]
				# nytimesDoc.news_desk = article["news_desk"]
				# nytimesDoc.section_name = article["section_name"]
				# nytimesDoc.subsection_name = article["subsection_name"]
				# nytimesDoc.type_of_material = article["type_of_material"]
				# nytimesDoc.article_id = article["_id"]
				# nytimesDoc.word_count = article["word_count"]

				# nytimesDoc.byline = article["byline"]
				# nytimesDoc.multimedia = article["multimedia"]
				# nytimesDoc.keywords = article["keywords"]

				# nytimesDoc.social_shares = shares.get_social_counts(nytimesDoc.web_url)

				nytimesDoc.content = get_nyt_data(nytimesDoc.web_url)
				nytimesDoc.save()
				print nytimesDoc.id
			except NotUniqueError:
				print nytimesDoc.web_url +" already exists.."
			# break

		# if page_num == 10:
		# 	break
		# break

	return `page_num`

@mod_data.route('/parse-social-shares')
def parse_social_shares():
	articles = JNYTDocument.objects(source="The New York Times")
	index = 0
	for article in articles:
		if not article.social_shares:
			print index
			article.social_shares = shares.get_social_counts(article.web_url)
			article.save()
			index += 1
		# break
	return "Done"

@mod_data.route('/compute-leniency')
def compute_liniency():
	bo = politicalLeaning.Bias()
	index = 0

	# for article in JNYTDocument.objects(source="DailyKos"):
	# 	print article.web_url
	# 	article.computed_political_leaning = "Unknown"
	# 	article.political_leaning_strength = 0
	# 	break
		# if article.computed_political_leaning != "Unknown":
			# print article.headline, "|", article.computed_political_leaning, "|", article.political_leaning_strength, "|"
			# label = bo.getPoliticalLeaning([article.headline, article.content])
			# print "Computed", label
			# break

	#Preprocessing step..
	# for article in JNYTDocument.objects:
	# 	print index
	# 	article.computed_political_leaning = "Unknown"
	# 	article.political_leaning_strength = 0
	# 	article.save()
	# 	print article.computed_political_leaning
	# 	index += 1

	for article in JNYTDocument.objects(source="WizBang Blog"):
		if article.computed_political_leaning != "Unknown":
			print article.source, article.headline, article.computed_political_leaning, article.political_leaning_strength
			continue

		if article.content != None and len(article.content.strip()) != 0:
			label = bo.getPoliticalLeaning([article.headline, article.content])
			article.computed_political_leaning = label[0]
			article.political_leaning_strength = label[1]
			article.save()
			print article.source, article.headline, article.computed_political_leaning, article.political_leaning_strength
		index += 1
		# break
	return "Anand"

@mod_data.route("/clean-data")
def clean_data():
	for article in JNYTDocument.objects:
		content = article.content
		if content != None:
			content = content.replace("\n","")
			content = content.strip()
			article.content = content
			article.save()

		print content
		# print article.source, article.headline, article.computed_political_leaning, article.political_leaning_strength




