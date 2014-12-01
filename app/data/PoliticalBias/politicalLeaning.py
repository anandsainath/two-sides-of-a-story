from __future__ import division
from nltk import word_tokenize,sent_tokenize
from collections import defaultdict
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import numpy
import util
from nltk import word_tokenize,sent_tokenize
from sets import Set
import numpy as np
import jsonrpc
from simplejson import loads
import os

server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
                             jsonrpc.TransportTcpIp(addr=("127.0.0.1", 3456)))
class Bias():
	def __init__(self):
		self.classifier = util.unpickle(os.path.dirname(os.path.realpath(__file__)) + "/cl.txt")
		self.featurenum = util.unpickle(os.path.dirname(os.path.realpath(__file__)) + "/featurenum.txt")
		print "Learner initialized"

	def getFeatures(self,doc):
		stop = stopwords.words('english')
		lmtzr = PorterStemmer()
		punctpattern = re.compile("[?!.-;,:]+")
		numberPattern = re.compile("[0-9]+")
		headline = doc[0]
		#headline features
		features = defaultdict(int)
		result = {}
		try:
			result = loads(server.parse(headline))
		except:
			pass
		namedEntities = util.runNER(headline)
		
		# print namedEntities
		# raw_input()

		n1 = []
		for word in namedEntities:
			if len(word.split())>2:
				continue
			for word1 in word.split():
				n1.append(word1.lower())
		try:
			if 'sentences' in result:
				for i in xrange(len(result['sentences'][0]['dependencies'])):
					for word in result['sentences'][0]['dependencies'][i]:
						if word.lower() in n1: 
							features[(word.lower(),result['sentences'][0]['dependencies'][i][0])]  = 1
		except:
			pass

		hlen = 0
		for line in sent_tokenize(headline):
			s = word_tokenize(line)
			for word in s:
				if punctpattern.match(word)!=None:
					features['hpunct']+=1
				if word.istitle():
					features['hTitlecase']+= 1
				features[('huni',lmtzr.stem(word.lower().strip()))] = 1
			for i in xrange(len(s)-1):
				x1 = s[i].lower().strip()
				x2 = s[i+1].lower().strip()
				features[('hbi',(x1,x2))] = 1

			hlen += len(s)
		if len(sent_tokenize(headline))!=0:
			features['hlen'] = hlen/len(sent_tokenize(headline))
		content = doc[1]
		dlen = 0

		# print "Calling runNER"
		namedEntities = util.runNER(content)
		features['ner'] = len(namedEntities)

		# print namedEntities
		# raw_input()

		for line in sent_tokenize(content):
			unigrams = word_tokenize(line)
			for i in xrange(len(unigrams)):
				if punctpattern.match(unigrams[i])!=None:
					features['dpunct']+=1
				if unigrams[i] not in namedEntities and unigrams[i] not in stop:
					unigram = lmtzr.stem(unigrams[i].lower().strip())
					features[('duni',unigram)] = 1
				if i != len(unigrams)-1:
					if unigrams[i]+" "+unigrams[i+1] not in namedEntities:
						bigram= (unigrams[i].lower().strip(),unigrams[i+1].lower().strip())
						features[('dbi',bigram)] = 1
	#		trigrams = [(unigrams[i],unigrams[i+1],unigrams[i+2]) for i in range(len(unigrams)-2)]
	#		for i in xrange(len(trigrams)):
	#			features[('dtri',trigrams[i])]=1
			dlen+=len(unigrams)
		if len(sent_tokenize(content))!=0:
			features['dlen'] = dlen/len(sent_tokenize(content))

		return features

	def getPoliticalLeaning(self,doc):
		input = doc#[doc['headline'],doc['content']]
		feature = self.getFeatures(input)
		testing = np.zeros((len(self.featurenum)))
		m = 0
		for word in feature:
			if word in self.featurenum:
				testing[self.featurenum[word]] = feature[word]
		pl = 'Liberal'
		if self.classifier.predict(testing) == 2:
			pl = 'Conservative'
		return [pl,self.classifier.decision_function(testing)[0]]