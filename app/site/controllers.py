#Flask dependencies
from flask import Blueprint, request, render_template
from datetime import timedelta, date
from time import strftime
import csv
import re
import json
from random import randint

from app.data.models import JNYTDocument

# Define the blueprint: 'site', set its url prefix: app.url/
mod_site = Blueprint('site', __name__, url_prefix='/site')


#/*** Utils Function ***/

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

#End Utils

@mod_site.route('/')
def index():
	return render_template('/site/index.html')

@mod_site.route('/treemap')
def treemap():
	return render_template('/site/treemap.html')

@mod_site.route('/get-article-content/<post_id>')
def get_article_content(post_id):
	article = JNYTDocument.objects(id=post_id)

	if len(article) != 0:
		return json.dumps({
			'content' : article[0].content,
			'source': article[0].source,
			'link': article[0].web_url
		})

@mod_site.route('/get-treemap-data')
def get_treemap_data():
	dict_main_data = {"name":"Presidential Elections"}
	dict_children = {}

	source = None
	output_file_name = "presidential_temp.json"

	if source != None:
		articles = JNYTDocument.objects(source=source)
	else:
		articles = JNYTDocument.objects

	count = 0

	for article in articles:
		if article.source not in dict_children:
			dict_children[article.source] = {}
			dict_children[article.source]["Liberal"] = {"count":0, "shares":0}
			dict_children[article.source]["Conservative"] = {"count":0, "shares":0}
			dict_children[article.source]["Unknown"] = {"count":0, "shares":0}

		dict_children[article.source][article.computed_political_leaning]["count"] += 1
		dict_children[article.source][article.computed_political_leaning]["shares"] += get_agg_share_count(article)

	list_children = []
	for key, value in dict_children.iteritems():
		if key == None:
			continue

		are_counts_zero = True
		item = {"name": key}
		item_children = []
		for item_key, item_value in value.iteritems():
			if item_key == "Conservative" or item_key == "Liberal":
				if(item_value["count"] > 0):
					are_counts_zero = False
				item_children.append({"name":item_key, "count":item_value["count"], "shares":item_value["shares"]})

		if not are_counts_zero:
			item["children"] = item_children
			list_children.append(item)

	return json.dumps(list_children)


@mod_site.route('/get-data')
def get_data():
	start_date = date( year = 2011, month = 1, day = 1 )
	end_date = date( year = 2013, month = 5, day = 31 )

	dict_liberal = {}

	source = None
	political_leaning = "Conservative"
	output_file_name = "conservative.csv"

	if source != None:
		articles = JNYTDocument.objects(source=source)
	elif political_leaning != None:
		articles = JNYTDocument.objects(political_leaning=political_leaning)
	else:
		articles = JNYTDocument.objects
	
	count = 0

	for article in articles:
		if article.content == None or len(article.content.strip()) == 0:
			continue

		political_leaning = article.political_leaning
		if political_leaning == "Unknown":
			political_leaning = article.computed_political_leaning
			if political_leaning == "Unknown":
				continue

		# print article.source

		if article.pub_date != None and article.pub_date.date() >= start_date and article.pub_date.date() <= end_date:
			date_string = strftime("%Y-%m-%d", article.pub_date.date().timetuple())

			if date_string in dict_liberal:
				date_summary = dict_liberal[date_string]
			else:
				date_summary = {
				"count": 0, 
				"Liberal": 0, 
				"Conservative": 0, 
				"Liberal_strength": 0,
				"Liberal_strength_Max": 0,
				"Liberal_Max":0, 
				"Conservative_Max":0, 
				"Conservative_strength": 0,
				"Conservative_strength_Max": 0,
				"Liberal_id":"", 
				"Conservative_id":"",
				"Liberal_title":"",
				"Conservative_title":""
			}

			print article.social_shares, article.id

			article_agg_share_count = get_agg_share_count(article)

			if article_agg_share_count > date_summary[political_leaning+"_Max"]:
				date_summary[political_leaning+"_Max"] = article_agg_share_count
				date_summary[political_leaning+"_id"] = article.id
				date_summary[political_leaning+"_title"] = article.headline

			if article.political_leaning_strength != None and abs(article.political_leaning_strength) > date_summary[political_leaning+"_strength_Max"]:
				date_summary[political_leaning+"_strength_Max"] = abs(article.political_leaning_strength)
				date_summary[political_leaning+"_strength"] += article.political_leaning_strength

			date_summary["count"] = date_summary["count"] + 1
			date_summary[political_leaning] = date_summary[political_leaning] + article_agg_share_count
			dict_liberal[date_string] = date_summary
			print article.pub_date, start_date, end_date

		count += 1
		
	output_result = []
	for single_date in daterange(start_date, end_date):
		output_item = []

		key = strftime("%Y-%m-%d", single_date.timetuple())
		output_item.append(key)

		if key in dict_liberal:
			output_item.append(dict_liberal[key]["Liberal"])
			output_item.append(abs(dict_liberal[key]["Liberal_strength"]))
			output_item.append(dict_liberal[key]["Liberal_id"])
			output_item.append(re.sub(r'[^\x00-\x7f]',r' ',dict_liberal[key]["Liberal_title"]))
			output_item.append(dict_liberal[key]["Conservative"])
			output_item.append(dict_liberal[key]["Conservative_strength"])
			output_item.append(dict_liberal[key]["Conservative_id"])
			output_item.append(re.sub(r'[^\x00-\x7f]',r' ',dict_liberal[key]["Conservative_title"]))
		else:
			output_item.append(0)
			output_item.append(0)
			output_item.append('')
			output_item.append('')
			output_item.append(0)
			output_item.append(0)
			output_item.append('')
			output_item.append('')

		output_result.append(output_item)

	with open(output_file_name, "wb") as f:
		writer = csv.writer(f, dialect='excel')
		writer.writerows(output_result)


def get_agg_share_count(article):
	total_count = 0

	for key, value in article.social_shares.iteritems():
		if key == "Facebook":
			total_count += int(value["total_count"])
			# for key_fb, value_fb in value.iteritems():
				# total_count += int(value_fb)
		else:
			total_count += int(value)
	return total_count

@mod_site.route('/get-temp-data')
def temp_data():
	start_date = date( year = 2011, month = 1, day = 1 )
	end_date = date( year = 2013, month = 5, day = 31 )

	output_result = []
	for single_date in daterange(start_date, end_date):
		output_item = []
		output_item.append(strftime("%Y-%m-%d", single_date.timetuple()))
		output_item.append(randint(0, 100))
		output_item.append(randint(0, 100))
		output_result.append(output_item)

	with open("output.csv", "wb") as f:
		writer = csv.writer(f, dialect='excel')
		writer.writerows(output_result)

	return "output.csv generated.."