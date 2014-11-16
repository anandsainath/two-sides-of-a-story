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

@mod_data.route('/parse-dailykos')
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
	print `no_of_pages`

	time.sleep(10)

	for page_num in range(1, no_of_pages+1):
		#time.sleep(10)
		url = base_url + `page_num`
		print url
		soup = BeautifulSoup(utils.getData(url)).find("div",{"class":"ajax-form-results ajax-delay-load"})
		#print soup

		table_list = soup.find("table",{"class":"styled storiesAsGrid"})
		print "Table list parsed"

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
					dailyKosDoc.save()

					dailyKosDoc.social_shares = shares.get_social_counts(dailyKosDoc.web_url)
					dailyKosDoc.save()
					#print link.get_text()
					#print datetime.strptime(date.get_text(),'%m/%d/%Y')
					#print link['href']
		
		if page_num == 2:
			break
	return "Anand"
	#print soup.find("div",{"class":"ajax-form-results ajax-delay-load"}).find({"h4",{"class":"sub-head"}})
	#return "Anand"

@mod_data.route('/parse-nyt')
def parse_nyt():
	#TODO: Parse the date as a datetime field.
	#TODO: Change headline from dict to text
	
	JNYTDocument.drop_collection()
	params = "US+Presidential+Election&begin_date=20120101&end_date=20121231"

	url = utils.get_nyt_article_search_url(params)
	response = urlopen(url).read()
	response = json.loads(response)

	print "Got response from nytimes"

	for article in response["response"]["docs"]:
		nytimesDoc = JNYTDocument()
		nytimesDoc.web_url = article["web_url"]
		nytimesDoc.snippet = article["snippet"]
		nytimesDoc.lead_paragraph = article["lead_paragraph"]
		nytimesDoc.abstract = article["abstract"]
		nytimesDoc.print_page = article["print_page"]
		nytimesDoc.source = article["source"]
		nytimesDoc.pub_date = article["pub_date"]
		nytimesDoc.document_type = article["document_type"]
		nytimesDoc.news_desk = article["news_desk"]
		nytimesDoc.section_name = article["section_name"]
		nytimesDoc.subsection_name = article["subsection_name"]
		nytimesDoc.type_of_material = article["type_of_material"]
		nytimesDoc.article_id = article["_id"]
		nytimesDoc.word_count = article["word_count"]

		nytimesDoc.byline = article["byline"]
		nytimesDoc.headline = article["headline"]
		nytimesDoc.multimedia = article["multimedia"]
		nytimesDoc.keywords = article["keywords"]
		nytimesDoc.save()

		print "Saved intermediate instance"
		print "getting_social_shares for :"+ nytimesDoc.web_url

		nytimesDoc.social_shares = shares.get_social_counts(nytimesDoc.web_url)
		nytimesDoc.save()

	return response["status"]