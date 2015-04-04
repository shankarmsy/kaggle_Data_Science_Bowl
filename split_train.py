from datetime import datetime
from csv import DictReader
from math import exp, log, sqrt
import os
import hickle
# TL; DR, the main training process starts on line: 250,
# you may want to start reading the code from there


##############################################################################
# parameters #################################################################
##############################################################################

# A, paths
# train = 'train.csv'               # path to training file
# test = 'test.csv'                 # path to testing file
# trainvw = 'train.vw'  # path of output file for vowpal wabbit
# testvw = 'test.vw'  # path of output file for vowpal wabbit

trainvw = 'train.vw'  # path of output file for vowpal wabbit
cv='cv.vw'
# testvw = 'test.vw'  # path of output file for vowpal wabbit

def data(path):
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

    for t, row in enumerate(DictReader(open(path))):
        outrow,features="",""

        click = 1
    	if 'click' in row:
    		if row['click'] == '0':
    			click=-1
        	del row['click']

        del row['id']

        # extract date
        date = int(row['hour'][4:6])

        # turn hour really into hour, it was originally YYMMDDHH
        # extract date
        row['date'] = int(row['hour'][4:6])
        row['hour'] = row['hour'][6:]

        features=features.join([" {0}_{1}".format(i+1, row[key]) for i, key in enumerate(row)])
        		# print outrow.join([key,':',str(value)])
        		# outrow=outrow.join([key,':',str(value)])

        outrow=outrow.join([str(click), ' |catf', features])

        yield t, row['date'], outrow


##############################################################################
# start training #############################################################
##############################################################################

start = datetime.now()
infiles=[train, test]
outfiles=[trainvw, testvw]
procdate=0

for t, date, outrow in data('train.csv'):  # data is a generator
    trfile =str.join(str(date),['train','.vw'])

    if not os.path.exists(trfile):
        outfile=open(trfile, 'w')

    outfile.write('%s\n' %outrow)
