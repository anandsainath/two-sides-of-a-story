#Flask dependencies
from flask import Blueprint, request
from urllib import urlopen

import json
from app.data.models import JNYTDocument
import shares, utils, time
from bs4 import BeautifulSoup
from datetime import datetime

# Define the blueprint: 'data', set its url prefix: app.url/data
mod_data = Blueprint('data', __name__, url_prefix='/data')

@mod_data.route('/')
def index():
	return utils.get_nyt_article_search_url("US+Presidential+Election&begin_date=20120101&end_date=20121231")

##Conservative Blogs

@mod_data.route('/conservative/parse-pjmedia')
def parse_pj_media():
	JNYTDocument.drop_collection()
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
			pjMediaDoc.social_shares = shares.get_social_counts(pjMediaDoc.web_url)
			pjMediaDoc.save()

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
	JNYTDocument.drop_collection()
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
			michelleMalkinDoc.social_shares = shares.get_social_counts(michelleMalkinDoc.web_url)
			michelleMalkinDoc.save()

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

@mod_data.route('/liberal/parse-dailykos')
def parse_dailykos():
	JNYTDocument.drop_collection()
	
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

	for page_num in range(1, no_of_pages+1):
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
					dailyKosDoc.social_shares = shares.get_social_counts(dailyKosDoc.web_url)
					dailyKosDoc.save()
					
					#Getting the content of the URL
					content_soup = BeautifulSoup(utils.getData(dailyKosDoc.web_url)).find("div",{"id":"storyWrapper"}).find("div",{"class":"article-body"})
					dailyKosDoc.content = content_soup.get_text()
					dailyKosDoc.save()
					#break
		#if page_num == 2:
		#	break
	return `page_num`

@mod_data.route('/parse-nyt')
def parse_nyt():
	JNYTDocument.drop_collection()
	params = "US+Presidential+Election&begin_date=20120101&end_date=20121231"

	url = utils.get_nyt_article_search_url(params)
	response = urlopen(url).read()
	response = json.loads(response)

	for article in response["response"]["docs"]:
		nytimesDoc = JNYTDocument()
		nytimesDoc.web_url = article["web_url"]
		nytimesDoc.snippet = article["snippet"]
		nytimesDoc.lead_paragraph = article["lead_paragraph"]
		nytimesDoc.abstract = article["abstract"]
		nytimesDoc.print_page = article["print_page"]
		nytimesDoc.source = article["source"]
		nytimesDoc.pub_date = datetime.strptime(article["pub_date"],'%Y-%m-%dT%H:%M:%SZ')
		nytimesDoc.document_type = article["document_type"]
		nytimesDoc.news_desk = article["news_desk"]
		nytimesDoc.section_name = article["section_name"]
		nytimesDoc.subsection_name = article["subsection_name"]
		nytimesDoc.type_of_material = article["type_of_material"]
		nytimesDoc.article_id = article["_id"]
		nytimesDoc.word_count = article["word_count"]

		nytimesDoc.byline = article["byline"]
		nytimesDoc.headline = article["headline"]['main']
		nytimesDoc.multimedia = article["multimedia"]
		nytimesDoc.keywords = article["keywords"]
		nytimesDoc.save()

		print "Saved intermediate instance"
		print "getting_social_shares for :"+ nytimesDoc.web_url

		nytimesDoc.social_shares = shares.get_social_counts(nytimesDoc.web_url)
		nytimesDoc.save()

	return response["status"]