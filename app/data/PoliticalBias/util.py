import nltk
import urllib2
import zlib
import time
import re
import cPickle as pickle
def prepareSentence(sample):
	sentences = nltk.sent_tokenize(sample)
	tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
	tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
	#chunked_sentences = nltk.batch_ne_chunk(tagged_sentences, binary=True)
	chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
	chunked_sentences_list = []
	try:
		chunked_sentences_list.append(next(chunked_sentences))
	except StopIteration:
		pass

	# print chunked_sentences_list
	return chunked_sentences_list

# Extract phrases from a parsed (chunked) tree
# Phrase = tag for the string phrase (sub-tree) to extract
# Returns: List of deep copies;  Recursive
def ExtractPhrases( myTree, phrase):
	myPhrases = []
	# print myTree, "myTree", myTree.label()
	if (myTree.label() == phrase):
		myPhrases.append(' '.join([child[0] for child in myTree]))
	for child in myTree:
		if (type(child) is nltk.tree.Tree):
			list_of_phrases = ExtractPhrases(child, phrase)
			if (len(list_of_phrases) > 0):
				myPhrases.extend(list_of_phrases)
	return myPhrases
 
# def extract_entity_names(t):
# 	entity_names = []

# 	print t, type(t)
# 	if hasattr(t, 'node') and t.node:
# 		print t.node, "Node Name"
# 		if t.node == 'NE':
# 			entity_names.append(' '.join([child[0] for child in t]))
# 		else:
# 			for child in t:
# 				entity_names.extend(extract_entity_names(child))
# 	return entity_names
 
def runNER(line):
	entity_names = []
	chunkedSentences = prepareSentence(line)
	for tree in chunkedSentences:
		# entity_names.extend(extract_entity_names(tree))
		entity_names.extend(ExtractPhrases(tree, "NE"))
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