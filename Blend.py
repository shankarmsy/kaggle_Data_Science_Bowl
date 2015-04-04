from datetime import datetime
from csv import DictReader
from math import exp, log, sqrt
import os, csv, glob, subprocess
from collections import OrderedDict

# TL; DR, the main training process starts on line: 250,
# you may want to start reading the code from there


##############################################################################
# parameters #################################################################
##############################################################################

# A, paths
outfile = 'best_blend3.csv'                 # path to testing file
# trainvw = 'train.vw'  # path of output file for vowpal wabbit
# testvw = 'test.vw'  # path of output file for vowpal wabbit

def data(i_f):
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
    for t,row in enumerate(DictReader(open(path))):
        # print "here"
        # a=[x.next()['click'] for x in i_f]
        # a=sum(float(a))
        yield row['id'], float(row['click'])


##############################################################################
# start training #############################################################
##############################################################################


start = datetime.now()
files=glob.glob('sub*.csv')
# files=['fc-morph-aug-v1.csv',
#        'fc-morph-aug-v2.csv',
#        'fc-morph-aug-v3.csv',
#        'fc2-morph-aug-v1.csv']
# for i,filenm in enumerate(files):
#     if 'blend' or 'sample' in filenm:
#         del files[i]

# print files

sub_file=csv.reader(open('sampleSubmission.csv'))
head=sub_file.next()

i_f=[DictReader(open(filenm)) for filenm in files]

no_of_preds=len(i_f)
row_count = int(subprocess.check_output('wc -l {}'.format(files[0]),shell=True).split()[-2])-1

o_f=open(outfile,'wb')
writer=csv.writer(o_f)
writer.writerow(head)
# print_key='siphonophore_physonect'

for i in range(row_count):  # data is a generator
    merged={}
    for x in i_f:
        temp=x.next()
        if not merged:
           merged=temp
           # print merged['image']
           # print print_key
           # print merged[print_key]
        else:
            # print temp[print_key]
            for key,value in temp.items():
                if key!='image':
                    merged[key]=float(merged[key])+float(value)
    # print "merged"
    for key, value in merged.items():
        if key!='image':
            merged[key]=float(value)/len(files)

    # print merged[print_key]

    out=[v for k,v in sorted(merged.items(), key=lambda i:head.index(i[0]))]
    writer.writerow(out)
    # break
    
    
