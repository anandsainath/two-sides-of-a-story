from app import db

class JNYTMultimedia(db.EmbeddedDocument):

	width = db.IntField()
	height = db.IntField()
	url = db.StringField()
	subtype = db.StringField()
	_type = db.StringField()

class JNYTDocument(db.Document):
	# __CollectionName__ = "immigration_reform_document_corpus"
	__CollectionName__ = "gun_control_document_corpus"
	# __CollectionName__ = "presidential_elections_document_corpus"

	web_url = db.StringField(required=True)
	snippet = db.StringField()
	lead_paragraph = db.StringField()
	abstract = db.StringField()
	print_page = db.IntField()
	source = db.StringField() #The New York Times, DailyKos

	##main content fields
	content = db.StringField()
	political_leaning = db.StringField(default="Unknown") # Liberal, Conservative, Unknown
	political_leaning_strength = db.FloatField()
	computed_political_leaning = db.StringField(default="Unknown")
	
	multimedia = db.ListField(db.DictField())
	headline = db.StringField()
	keywords = db.ListField(db.DictField())
	byline = db.DictField()
	
	pub_date = db.DateTimeField()
	document_type = db.StringField()
	news_desk = db.StringField()
	section_name = db.StringField()
	subsection_name = db.StringField()
	type_of_material = db.StringField()
	article_id = db.StringField()
	word_count = db.IntField()

	social_shares = db.DictField()

	meta = {
		'collection' : __CollectionName__,
		'allow_inheritance': True
	}
