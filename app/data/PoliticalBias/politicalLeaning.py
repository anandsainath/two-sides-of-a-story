from __future__ import division
import nltk
from nltk import word_tokenize,sent_tokenize
from collections import defaultdict
import re
import sets
import nltk.classify
from sklearn.svm import LinearSVC
from sklearn import cross_validation
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk.metrics
import nltk
from random import randint
import collections
import numpy
import cPickle as pickle
import util
from nltk import word_tokenize,sent_tokenize
import os,sys
from getData import Data
from sklearn.linear_model import LogisticRegression
from sets import Set
from scipy.sparse import csr_matrix
from scipy.sparse import lil_matrix
import numpy as np

class Bias():
	def __init__(self):
		self.classifier = util.unpickle("cl.txt")
		self.featurenum = util.unpickle("featurenum.txt")

	def getFeatures(self,doc):
		stop = stopwords.words('english')
		lmtzr = PorterStemmer()
		punctpattern = re.compile("[?!.-;,:]+")
		numberPattern = re.compile("[0-9]+")
		headline = doc[0]
		features = defaultdict(int)
		x = 0
		for line in sent_tokenize(headline):
			s = word_tokenize(line)
			for word in s:
				if punctpattern.match(word)!=None:
					features['hpunct']+=1
				if word.istitle():
					features['hTitlecase']+= 1
				if word.lower().strip() not in stop:
					features[('huni',lmtzr.stem(word.lower().strip()))] = 1
			for i in xrange(len(s)-1):
				x1 = lmtzr.stem(s[i].lower().strip())
				x2 = lmtzr.stem(s[i+1].lower().strip())
				features[('hbi',(x1,x2))] = 1
			x += len(s)
		features['hlen'] = x/len(sent_tokenize(headline))
		content = doc[1]
		x = 0
		for line in sent_tokenize(content):
			unigrams = word_tokenize(line)
			for i in xrange(len(unigrams)):

				if unigrams[i].istitle():
					features['dTitle']+=1
				if numberPattern.match(unigrams[i])!=None:
					features['dnumb']+=1
				if punctpattern.match(unigrams[i])!=None:
					features['dpunct']+=1
				if unigrams[i].lower().strip() not in stop:
					unigrams[i] = lmtzr.stem(unigrams[i].lower().strip())
					features[('duni',unigrams[i])] = 1
				else:
					unigrams[i] = lmtzr.stem(unigrams[i].lower().strip())
			
			bigrams= [(unigrams[i],unigrams[i+1]) for i in range(len(unigrams)-1)]
			for i in xrange(len(bigrams)):
				features[('dbi',bigrams[i])] = 1
			trigrams = [(unigrams[i],unigrams[i+1],unigrams[i+2]) for i in range(len(unigrams)-2)]
			for i in xrange(len(trigrams)):
				features[('dtri',trigrams[i])]=1
			x+=len(unigrams)
		features['dlen'] = x/len(sent_tokenize(content))

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