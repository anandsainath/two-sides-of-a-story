import nltk
import urllib2
import simplejson
import zlib
import time
import re
import cPickle as pickle
def prepareSentence(sample):
	sentences = nltk.sent_tokenize(sample)
	tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
	tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
	chunked_sentences = nltk.batch_ne_chunk(tagged_sentences, binary=True)
	return chunked_sentences
 
def extract_entity_names(t):
	entity_names = []
	if hasattr(t, 'node') and t.node:
		if t.node == 'NE':
			entity_names.append(' '.join([child[0] for child in t]))
		else:
			for child in t:
				entity_names.extend(extract_entity_names(child))
	return entity_names
 
def runNER(line):
	entity_names = []
	chunkedSentences = prepareSentence(line)
	for tree in chunkedSentences:
		entity_names.extend(extract_entity_names(tree))

	return set(entity_names)

def runPOS(line):
		return nltk.pos_tag(nltk.word_tokenize(line))

def unpickle(filename):
	f = open(filename,"rb") 
	heroes = pickle.load(f)
	return heroes

def writePickle(struct, filename):
	file1 = open(filename,"wb") 			
	pickle.dump(struct,file1)
	file1.close()