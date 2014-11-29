#Flask dependencies
from flask import Blueprint, request, render_template
from datetime import timedelta, date
from time import strftime
import csv
from random import randint

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