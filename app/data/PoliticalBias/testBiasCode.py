import politicalLeaning
from getData import Data

d = Data()
liberalData = d.getData('Liberal')
conservativeData = d.getData('Conservative')
bo = politicalLeaning.Bias()
num = 0
for id in liberalData:
	print 'Liberal',num
	print bo.getPoliticalLeaning(liberalData[id])
	num+=1	
	if num == 10:
		break

for id in conservativeData:
	print 'Conservative',num
	print bo.getPoliticalLeaning(conservativeData[id])
	num+=1	
	if num == 20:
		break