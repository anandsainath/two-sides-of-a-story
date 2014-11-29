#Flask dependencies
from flask import Blueprint, request, render_template
from datetime import timedelta, date
from time import strftime
import csv
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

@mod_site.route('/get-data')
def get_data():
	start_date = date( year = 2011, month = 1, day = 1 )
	end_date = date( year = 2013, month = 5, day = 31 )

	dict_liberal = {}

	articles = JNYTDocument.objects
	count = 0

	for article in articles:
		if article.political_leaning == "Unknown":
			continue
		if article.pub_date != None and article.pub_date.date() >= start_date and article.pub_date.date() <= end_date:
			date_string = strftime("%Y-%m-%d", article.pub_date.date().timetuple())

			if date_string in dict_liberal:
				date_summary = dict_liberal[date_string]
			else:
				date_summary = {"count": 0, "Liberal": 0, "Conservative": 0}

			date_summary["count"] = date_summary["count"] + 1
			date_summary[article.political_leaning] = date_summary[article.political_leaning] + get_agg_share_count(article)
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
			output_item.append(dict_liberal[key]["Conservative"])
		else:
			output_item.append(0)
			output_item.append(0)

		output_result.append(output_item)

	with open("output.csv", "wb") as f:
		writer = csv.writer(f, dialect='excel')
		writer.writerows(output_result)


def get_agg_share_count(article):
	total_count = 0

	for key, value in article.social_shares.iteritems():
		if key == "Facebook":
			for key_fb, value_fb in value.iteritems():
				total_count += int(value_fb)
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