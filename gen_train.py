import os
import sys
import subprocess
import numpy as np

def imageaug(folder,aug):
    # aug=np.random.choice(distortions)
    aug_cmd="find {} -iname '*.jpg' -exec mogrify {}".format(folder,aug)+" {} +"
    print "Batch augmenting images based on %s" %(aug)
    print "Executing %s" %aug_cmd
    os.system(aug_cmd)

def resize(folder, res):
    res_cmd="find {} -iname '*.jpg' -exec mogrify -resize {} -gravity center -background white -extent {}".format(folder,res,res)+" {} +"
    # res_cmd="find {} -iname '*.jpg' -exec mogrify -resize {}\!".format(folder,res)+" {} +"
    print "batch resizing images to %s" %(res)
    print "Executing %s" %res_cmd
    os.system(res_cmd)


if len(sys.argv) < 5:
    print "Usage: python gen_train.py input_folder output_folder aug resolution"
    exit(1)

fi = sys.argv[1]
fo = sys.argv[2]
transforms=[]
augment=sys.argv[3]
resolution=sys.argv[4]
dist_parm=sys.argv[5]

if fi==fo:
    print "Resizing Input - skipping image copy"
else:
    print "Copying Images from %s to %s" %(fi,fo)
    cmd="find {} -name '*'".format(fi)+" -exec cp -r '{}'"+" {} \;".format(fo)
    print "Executing %s" %cmd
    os.system(cmd)
    # os.system("cp -r {}* {}".format(fi,fo))

if augment=='y':
    imageaug(fo,dist_parm)
    resize(fo,resolution)
else:
    resize(fo,resolution)

# classes = os.listdir(fi)

# os.chdir(fo)
# for cls in classes:
#     try:
#         os.mkdir(cls)
#     except:
#         pass
#     imgs = os.listdir(fi + cls)
#     for img in imgs:
#         if augment=='y':
#            cmd = "convert "+rand[np.random.random_integers(len(rand))]
#         else:
#            cmd = "convert -resize {} -gravity center -background white -extent {} ".format(resolution,resolution)
#         md = ""

# find /data/dbowl/train/ -iname '*.jpg' -exec mogrify -resize 48x48 -gravity center -background white -extent 48x48 {} +

#         md += "find "+fo+"/ -iname '''*.jpg''' "+cmd
#         md += fi + cls + "/" + img
#         md += " " + fo + cls + "/" + img
#         os.system(md)


#         # md += cmd
#         # md += fi + cls + "/" + img
#         # md += " " + fo + cls + "/" + img
#         # os.system(md)

#         if augment=='y':
#             of=fo + cls + "/" + img
#             ofsize=subprocess.check_output("identify -format '''%wx%h''' {}".format(of),shell=True).split('\n')[-2]

#             if ofsize.strip()!=resolution:
#                 cmd = "convert -resize {} -gravity center -background white -extent {} ".format(resolution,resolution)
#                 md = ""
#                 md += cmd
#                 md += fo + cls + "/" + img
#                 md += " " + fo + cls + "/" + img
#                 os.system(md)
