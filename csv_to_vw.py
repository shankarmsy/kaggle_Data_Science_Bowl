from datetime import datetime
from csv import DictReader
from math import exp, log, sqrt
import hickle
import numpy as np

# TL; DR, the main training process starts on line: 250,
# you may want to start reading the code from there


##############################################################################
# parameters #################################################################
##############################################################################

# A, paths
train = 'train.csv'               # path to training file
test = 'test.csv'                 # path to testing file
# trainvw = 'train.vw'  # path of output file for vowpal wabbit
# testvw = 'test.vw'  # path of output file for vowpal wabbit

trainvw = 'train.vw'  # path of output file for vowpal wabbit
testvw = 'test.vw'  # path of output file for vowpal wabbit

def data(X):
    ''' GENERATOR: Apply hash-trick to the original csv row
                   and for simplicity, we one-hot-encode everything

        INPUT:
            path: path to training or testing file
            D: the max index that we can hash to

        YIELDS:
            ID: id of the instance, mainly useless
            x: a list of hashed and one-hot-encoded 'indices'
               we only need the index since all values are either 0 or 1
            y: y = 1 if we have a click, else we have y = 0
    '''

    for t, row in enumerate(X):
        outrow,features="",""

        features=features.join([" {0}:{1}".format(c+1, X[i+1]) for (r,c), value in enumerate(row)])
        		# print outrow.join([key,':',str(value)])
        		# outrow=outrow.join([key,':',str(value)])

        outrow=outrow.join([str(click), ' |catf', features])

        yield t, row['date'], outrow


##############################################################################
# start training #############################################################
##############################################################################

start = datetime.now()
files=['train.hkl','test.hkl']

for i in range(2):
	X = hickle.load(files[i])
	for t, date, outrow in data(X):  # data is a generator
                    # if t>10:
                    #     break

                    if t % 1000000 == 0 and t > 0:
                        print("Done writing %d rows from file %s. Time elapsed:%s"%(t, path, str(datetime.now() - start)))

                    outfile.write('%s\n' %outrow)

	print("File %s for vw ready. Final Row count %d. Time elapsed:%s"%(outfiles[i], t, str(datetime.now() - start)))

