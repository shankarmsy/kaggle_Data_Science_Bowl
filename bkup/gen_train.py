import os
import sys
import subprocess
import numpy as np

rand={
1:"-rotate 45 ",
2:"-rotate 90 ",
3:"-rotate 135 ",
4:"-rotate 180 ",
5:"-rotate 225 ",
6:"-rotate 270 ",
7:"-rotate 315 ",
8:"-transpose ",
9:"-transverse ",
10:"-normalize ",
}

if len(sys.argv) < 4:
    print "Usage: python gen_train.py input_folder output_folder aug"
    exit(1)

fi = sys.argv[1]
fo = sys.argv[2]
transforms=[]
augment=sys.argv[3]

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
           cmd = "convert -resize 48x48 -gravity center -background white -extent 48x48 "
        md = ""
        md += cmd
        md += fi + cls + "/" + img
        md += " " + fo + cls + "/" + img
        os.system(md)

        if augment=='y':
            cmd = "convert -resize 48x48 -gravity center -background white -extent 48x48 "
            md = ""
            md += cmd
            md += fo + cls + "/" + img
            md += " " + fo + cls + "/" + img
            os.system(md)




