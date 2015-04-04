import os
from time import sleep

if raw_input('Delete models? ')=='y':
    os.system('rm -rf /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/*')

for iter in range(int(raw_input('Epochs: '))):
    print "Starting epoch %d" %(iter+1)
    print "Deleting images"
    os.system('rm -rf /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/*')
    os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.lst')
    os.system('rm /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/train.bin')
    print "Augementing and resizing images to 48x48"
    os.system('python gen_train.py /data/dbowl/train/ /data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/data/train/ y')
    print "Generating Image list"
    os.system('python gen_img_list.py train /data/dbowl/sampleSubmission.csv data/train/ train.lst')
    print "Generating Binaries"
    os.system('/data/dbowl/cxxnet/cxxnet/tools/im2bin train.lst ./ train.bin')
    if iter==0:
        os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf max_round=10')
    else:
        print('Please provide model input in 10 seconds! (Hit Ctrl-C to start)')
        try:
            for i in range(0,20):
                sleep(1)
                print('No input is given.')
        except KeyboardInterrupt:
            model_in=raw_input('Model# ')

        if model_in=='':
            model_in='0010'

        os.system('/data/dbowl/cxxnet/cxxnet/bin/cxxnet bowl.conf max_round=10 model_in=/data/dbowl/cxxnet/cxxnet/example/kaggle_bowl/models/{}.model'.format(model_in))
