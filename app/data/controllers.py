#Flask dependencies
from flask import Blueprint, request
from urllib import urlopen

import json
from app.data.models import JNYTDocument
import shares

# Define the blueprint: 'data', set its url prefix: app.url/data
mod_data = Blueprint('data', __name__, url_prefix='/data')

@mod_data.route('/')
def index():
	print shares.get_social_counts()
	return "Hello Data World!"

@mod_data.route('/parse-nyt')
def parse_nyt():
	JNYTDocument.drop_collection()
	url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?q=US+Presidential+Election&begin_date=20120101&end_date=20121231&api-key=318a69b2af97848f66071cb4c1fdc831:15:69992102"

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
		break

	return response["status"]