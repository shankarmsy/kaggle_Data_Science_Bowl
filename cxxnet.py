import os,random
from time import sleep
import realaug as ra
import numpy as np
# angle=np.random.random_integers(0,360)
# angles=[90,180,270]
# distortions=["-distort\ SRT\ {}\ ".format(x) for x in angles]
# distortions+=(["-shear\ {}\ ".format(x) for x in angles])
# distortions+=(["-flip\ ","-flop\ ","-transpose\ ","-transverse\ "])
# 2:"-distort SRT {},0 ".format(str(round(np.logspace(.7,1.3,num=1),1))),
# 8:"-distort SRT {},{} ".format(str(round(np.logspace(.7,1.3,num=1),1)),
                               # str(np.random.random_integers(0,360)))

# print distortions
# random.shuffle(distortions)
# print distortions
cont=raw_input('Continue Training? ')
resolution=raw_input('Resolution(l/w)? ')
# resize=raw_input('Resize Train? ')
if cont=='y':
    epochs=raw_input('How many Epochs: ')
    resize=delmod='n'
else:
    resize=raw_input('Resize Input? ')
    delmod=raw_input('Delete models? ')
    epochs=raw_input('Epochs: ')

def img_resize(mode, res):
    if mode=="train":
        folder="/data/dbowl/train"
    else:
        folder="/data/dbowl/test"

    print "batch resizing %s to %s" %(mode,res)
    res_cmd="find {} -iname '*.jpg' -exec mogrify -resize {} -gravity center -background white -extent {}".format(folder,res,res)+" {} +"
    # res_cmd="find {} -iname '*.jpg' -exec mogrify -resize {}\!".format(folder,res)+" {} +"

    print "Executing %s" %res_cmd
    os.system(res_cmd)

def train_cxxnet():
    # print('Please provide model input in 10 seconds! (Hit Ctrl-C to start)')
    # model_in=''
    # try:
    #     for i in range(0,5):
    #         sleep(1)
    #         print('No input is given.')
    # except KeyboardInterrupt:
    #     model_in=raw_input('Model# ')

    # if model_in=='':
    #     model_in='00{}'.format(epochs)

    # os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf max_round=1 continue=1')

    os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf num_rounds=1  model_in=/data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/0001.model')

def build_model():
    for i in range(int(epochs)):
        print "Deleting images"

        os.system('rm -rf /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/*')
        os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/image_mean.bin')
        os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.lst')
        os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.bin')

        # if 'SRT' in item:
        #     for j,angle in enumerate(angles):
        #         cur_rot=item.format(angle)
        #         print "Augmenting with {} and resizing images to {}".format(cur_rot,resolution)
        #         os.system("python gen_train.py /data/dbowl/train/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/ y {} {}".format(resolution,cur_rot))
        #         train_cxxnet()
        # else:
        print "Starting Augmentation for Epoch %s" %(i+1)
        os.system('python realaug.py /data/dbowl/train/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/ {} train 0.0 0.0 0.0'.format(resolution))
        print "Generating Image list"
        os.system('python gen_img_list.py train /data/dbowl/sampleSubmission.csv data/train/ train.lst')
        print "Generating Binaries"
        os.system('/data/dbowl/cxxnet/cxxnet/tools/im2bin train.lst ./ train.bin')

        if i==0 and cont!='y':
            os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf num_rounds=1')
        else:
            train_cxxnet()

def gen_predictions():
    augmentation_transforms = []
    i=1
    for zoom in [1 / 1.2, 1.0, 1.2]:
        for angle in np.linspace(0, 360, 10, endpoint=False):
            print "Starting Augmentation %s for Zoom %.2f Angle %.2f Shear 0" %(i,zoom,angle)
            os.system('python realaug.py /data/dbowl/test/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/test/ {} test {} {} 0'.format(resolution,angle,zoom))
            print "Generating Image list"
            os.system('python gen_img_list.py test /data/dbowl/sampleSubmission.csv data/test/ test.lst')
            print "Generating Binaries"
            os.system('/data/dbowl/cxxnet/cxxnet/tools/im2bin test.lst ./ test.bin')
            print "Predicting Augmentation %s" %(i)
            os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet pred.conf pred=test{}.txt'.format(str(i)))
            print "Generating CSV"
            os.system('python make_submission.py /data/dbowl/sampleSubmission.csv test.lst test{}.txt out{}.csv'.format(i,i))

            i+=1
            print "Starting Augmentation %s for Zoom %.2f Angle %.2f Shear 180" %(i,zoom,angle+180)
            os.system('python realaug.py /data/dbowl/test/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/test/ {} test {} {} 180'.format(resolution,angle+180,zoom))
            print "Generating Image list"
            os.system('python gen_img_list.py test /data/dbowl/sampleSubmission.csv data/test/ test.lst')
            print "Generating Binaries"
            os.system('/data/dbowl/cxxnet/cxxnet/tools/im2bin test.lst ./ test.bin')
            print "Predicting Augmentation %s" %(i)
            os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet pred.conf pred=test{}.txt'.format(str(i)))
            print "Generating CSV"
            os.system('python make_submission.py /data/dbowl/sampleSubmission.csv test.lst test{}.txt out{}.csv'.format(i,i))
            i+=1

if resize=='y':
   print "Resizing Input Images"
   img_resize('train','96x96')
   img_resize('test','96x96')

# if test=='y':
#     print "copying and resizing test"
#     os.system('python gen_train.py /data/dbowl/test/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/test/ n {} None'.format(resolution))

if delmod=='y':
    print "clearing models directory"
    os.system('rm -rf /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/*')

# print "First iteration with original images"
# os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.lst')
# os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.bin')
# os.system('cp -r /data/dbowl/train/* /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/')
# print "Generating Image list"
# os.system('python gen_img_list.py train /data/dbowl/sampleSubmission.csv data/train/ train.lst')
# print "Generating Binaries"
# os.system('/data/dbowl/cxxnet/cxxnet/tools/im2bin train.lst ./ train.bin')
# print "Training First iteration with original images"
# os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf max_round={}'.format(epochs))

    
print "Ready to Train"
build_model()

print "Ready to Generate Predictions"
gen_predictions()

print "Blending Predictions"
os.system('python Blend.py')
