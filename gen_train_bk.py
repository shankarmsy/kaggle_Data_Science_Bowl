import os
import sys
import subprocess
import numpy as np

rand={
1:"-distort SRT {} ".format(str(np.random.random_integers(0,360))),
2:"-distort SRT {},0 ".format(str(round(np.logspace(.7,1.3,num=1),1))),
3:"-shear {} ".format(str(np.random.random_integers(0,360))),
4:"-flip ",
5:"-flop ",
6:"-transpose ",
7:"-transverse ",
}

if len(sys.argv) < 5:
    print "Usage: python gen_train.py input_folder output_folder aug resolution"
    exit(1)

fi = sys.argv[1]
fo = sys.argv[2]
transforms=[]
augment=sys.argv[3]
resolution=sys.argv[4]

classes = os.listdir(fi)

os.chdir(fo)
for cls in classes:
    try:
        os.mkdir(cls)
    except:
        pass
    imgs = os.listdir(fi + cls)
    for img in imgs:
        if augment=='y':
           cmd = "convert "+rand[np.random.random_integers(len(rand))]
        else:
           cmd = "convert -resize {} -gravity center -background white -extent {} ".format(resolution,resolution)
        md = ""
        md += cmd
        md += fi + cls + "/" + img
        md += " " + fo + cls + "/" + img
        os.system(md)

        if augment=='y':
            of=fo + cls + "/" + img
            ofsize=subprocess.check_output("identify -format '''%wx%h''' {}".format(of),shell=True).split('\n')[-2]

            if ofsize.strip()!=resolution:
                cmd = "convert -resize {} -gravity center -background white -extent {} ".format(resolution,resolution)
                md = ""
                md += cmd
                md += fo + cls + "/" + img
                md += " " + fo + cls + "/" + img
                os.system(md)
