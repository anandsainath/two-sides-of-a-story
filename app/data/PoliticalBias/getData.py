import pymongo


class Data:
	def __init__(self):
		client = pymongo.MongoClient("localhost",12345)
		db = client.socomp
		self.collection = db.presidential_elections_document_corpus

	def getData(self,leaning):
		l = {}
		for doc in self.collection.find({'political_leaning':leaning}):
			if doc['_id'] not in l:
				if 'content' in doc:
					l[doc['_id']] = [doc['headline'],doc['content']]
		return l

	def getLiberalHeadlines(self):
		for doc in self.collection.find({'political_leaning':'Liberal'}):
			print doc

