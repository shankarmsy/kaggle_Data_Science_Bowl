# rotation_angles = [45, 90, 135, 180, 225, 270, 315]
rotation_angles = [90, 180, 270]
 
def create_image_rotations(image):
    imgs = [(image.rotate(a), a) for a in rotation_angles]
    return imgs

def create_image_flips(image):
    return [(image.transpose(Image.FLIP_LEFT_RIGHT), 'vflip'),
            (image.transpose(Image.FLIP_TOP_BOTTOM), 'hflip')] 
 
if __name__ == '__main__':
    import glob,os
    import sys
    from datetime import datetime
    from PIL import Image
    from skimage.io import imread
    # if len(sys.argv) >= 2:
    #     img_data = glob.glob(sys.argv[1])
    # else:
    #     raise ValueError('Must pass directory of images as the first parameter')
 
    # n_images = len(img_data)
    # print 'Processing %i images' % n_images
 
    start_time = datetime.now()

i=0
directory_names = list(set(glob.glob(os.path.join("train", "*")) ).difference(set(glob.glob(os.path.join("train","*.*")))))
 
for folder in directory_names:
# Append the string class name for each class
    for fileNameDir in os.walk(folder):   
        for fileName in fileNameDir[2]:
            i+=1
            imgf = "{0}{1}{2}".format(fileNameDir[0], os.sep, fileName)  
            img = Image.open(imgf)

            spimgf = imgf.split('/')
            image_path = '/'.join(spimgf[:-1])
            image_file = spimgf[-1].split('.')[0]
     
            rimgs = create_image_rotations(img)
            for rimg, rot in rimgs:
                rimg.save(image_path + '/' + image_file + '_rot' + str(rot) + '.jpg')

            rimgs = create_image_flips(img)
            for rimg, flip in rimgs:
                rimg.save(image_path + '/' + image_file + '_' + str(flip) + '.jpg')
                
            if ((i+1) % 10000) == 0:
                print 'Rotated %i files in %is' % (i+1, (datetime.now() - start_time).seconds)

# i=0
# directory_names = list(set(glob.glob(os.path.join("train", "*")) ).difference(set(glob.glob(os.path.join("train","*.*")))))
 
# for folder in directory_names:
# # Append the string class name for each class
#     for fileNameDir in os.walk(folder):   
#         for fileName in fileNameDir[2]:
#             i+=1
#             imgf = "{0}{1}{2}".format(fileNameDir[0], os.sep, fileName)  
#             img = Image.open(imgf)

#             spimgf = imgf.split('/')
#             image_path = '/'.join(spimgf[:-1])
#             image_file = spimgf[-1].split('.')[0]
     
#             rimgs = create_image_flips(img)
#             for rimg, flip in rimgs:
#                 rimg.save(image_path + '/' + image_file + '_' + str(flip) + '.jpg')

#             if ((i+1) % 10000) == 0:
#                 print 'Flipped %i files in %is' % (i+1, (datetime.now() - start_time).seconds)

