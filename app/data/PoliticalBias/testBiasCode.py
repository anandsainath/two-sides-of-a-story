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
