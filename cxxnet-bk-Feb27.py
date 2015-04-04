import os,random
from time import sleep

# angle=np.random.random_integers(0,360)
angles=[90,180,270]
distortions=["-distort\ SRT\ {}\ ".format(x) for x in angles]
# distortions+=(["-shear\ {}\ ".format(x) for x in angles])
# distortions+=(["-flip\ ","-flop\ ","-transpose\ ","-transverse\ "])
# 2:"-distort SRT {},0 ".format(str(round(np.logspace(.7,1.3,num=1),1))),
# 8:"-distort SRT {},{} ".format(str(round(np.logspace(.7,1.3,num=1),1)),
                               # str(np.random.random_integers(0,360)))

# print distortions
random.shuffle(distortions)
# print distortions

resolution=raw_input('Resolution? ')
resize=raw_input('Resize Train? ')
test=raw_input('Copy & Resize Test? ')
delmod=raw_input('Delete models? ')
epochs=raw_input('Epochs per distortion: ')

def train_cxxnet():
    print('Please provide model input in 10 seconds! (Hit Ctrl-C to start)')
    model_in=''
    try:
        for i in range(0,5):
            sleep(1)
            print('No input is given.')
    except KeyboardInterrupt:
        model_in=raw_input('Model# ')

    if model_in=='':
        model_in='00{}'.format(epochs)

    os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf max_round={} model_in=/data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/{}.model'.format(epochs,model_in))


if resize=='y':
    print "resizing original train images"
    os.system('python gen_train.py /data/dbowl/train/ /data/dbowl/train/ n {} None'.format(resolution))

if test=='y':
    print "copying and resizing test"
    os.system('python gen_train.py /data/dbowl/test/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/test/ n {} None'.format(resolution))

if delmod=='y':
    print "clearing models directory"
    os.system('rm -rf /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/*')

print "First iteration with original images"
os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.lst')
os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.bin')
os.system('cp -r /data/dbowl/train/* /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/')
print "Generating Image list"
os.system('python gen_img_list.py train /data/dbowl/sampleSubmission.csv data/train/ train.lst')
print "Generating Binaries"
os.system('/data/dbowl/cxxnet/cxxnet/tools/im2bin train.lst ./ train.bin')
print "Training First iteration with original images"
os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf max_round={}'.format(epochs))

for i,item in enumerate(distortions):
    print "Deleting images"
    os.system('rm -rf /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/*')
    # if 'SRT' in item:
    #     for j,angle in enumerate(angles):
    #         cur_rot=item.format(angle)
    #         print "Augmenting with {} and resizing images to {}".format(cur_rot,resolution)
    #         os.system("python gen_train.py /data/dbowl/train/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/ y {} {}".format(resolution,cur_rot))
    #         train_cxxnet()
    # else:
    print "Augmenting with {} and resizing images to {}".format(item, resolution)
    os.system('python gen_train.py /data/dbowl/train/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/ y {} {}'.format(resolution,item))
    train_cxxnet()
    # os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/image_mean.bin')
    
