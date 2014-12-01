import politicalLeaning
from getData import Data

d = Data()
# liberalData = d.getData('USA Today')
liberalData = d.getData('The New York Times')
#print liberalData
#conservativeData = d.getData('Conservative')
#print conservativeData
bo = politicalLeaning.Bias()
num = 0
for id in liberalData:

	print liberalData[id][0]
	print bo.getPoliticalLeaning(liberalData[id])
	num+=1	
	if num == 40:
		break

# for id in conservativeData:
# 	print 'Conservative',num
# 	print bo.getPoliticalLeaning(conservativeData[id])
# 	num+=1	
# 	if num == 20:
# 		break