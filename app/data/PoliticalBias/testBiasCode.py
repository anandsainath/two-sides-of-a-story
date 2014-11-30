import politicalLeaning
from getData import Data

d = Data()
# liberalData = d.getData('Liberal')
conservativeData = d.getData('The New York Times')
bo = politicalLeaning.Bias()
num = 0
conservative = 0
liberal = 0

conservative_title = []
liberal_title = []

for id in conservativeData:
	label =  bo.getPoliticalLeaning(conservativeData[id])
	if label[0] == "Conservative":
		conservative += 1
		if label[1] > 10:
			conservative_title.append(conservativeData[id][0])
	else:
		liberal += 1
		liberal_title.append(conservativeData[id][0])
	num+=1

print liberal, conservative, num
print liberal_title
print conservative_title