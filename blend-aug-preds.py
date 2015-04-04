import csv
import sys
import glob
import subprocess

if len(sys.argv) < 3:
    print "Usage: python make_submission.py sample_submission.csv test.lst out.csv"
    exit(1)

fc = csv.reader(file(sys.argv[1]))
fl = csv.reader(file(sys.argv[2]), delimiter='\t', lineterminator='\n')

files=glob.glob('test*.txt')
# i_f=[csv.reader(filenm, delimiter=' ', lineterminator='\n') for filenm in files]
i_f=[csv.reader(file(filenm), delimiter=' ', lineterminator='\n') for filenm in files]

fo = csv.writer(open(sys.argv[3], "w"), lineterminator='\n')

head = fc.next()
fo.writerow(head)

head = head[1:]

no_of_preds=len(i_f)
row_count = int(subprocess.check_output('wc -l {}'.format(files[0]),shell=True).split()[-2])-1

img_lst = []
for line in fl:
    path = line[-1]
    path = path.split('/')
    path = path[-1]
    img_lst.append(path)

for idx in range(row_count):
    merged=[]
    for test_file in i_f:
        temp=test_file.next()
        if not merged:
           merged=temp
           merged=merged[:-1]
        else:
           for i,item in enumerate(temp):
               if item!='':
                  merged[i]=float(merged[i])+float(item)

    # print merged
    newline=[float(item)/no_of_preds for item in merged]
    # print img_lst[idx]
    # print newline
    row = [img_lst[idx]]
    # merged = merged[:-1]
    row.extend(newline)
    # print row
    fo.writerow(row)

    

