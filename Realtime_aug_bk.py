import glob,os
from joblib import Parallel, delayed
import joblib
import sys
from datetime import datetime
import skimage
from skimage.io import imread, imsave
from pylab import cm
from skimage.transform import AffineTransform, SimilarityTransform, warp, resize
import numpy as np

start_time = datetime.now()

default_augmentation_params = {
    'zoom_range': (1.0, 1.1),
    'rotation_range': (0, 360),
    'shear_range': (0, 0),
    'translation_range': (-4, 4),
}

def build_ds_transform(ds_factor=1.0, orig_size=None, target_size=(48, 48), do_shift=True, subpixel_shift=False):
    rows, cols = orig_size
    trows, tcols = target_size
    col_scale = row_scale = ds_factor
    src_corners = np.array([[1, 1], [1, rows], [cols, rows]]) - 1
    dst_corners = np.zeros(src_corners.shape, dtype=np.double)
    # take into account that 0th pixel is at position (0.5, 0.5)
    dst_corners[:, 0] = col_scale * (src_corners[:, 0] + 0.5) - 0.5
    dst_corners[:, 1] = row_scale * (src_corners[:, 1] + 0.5) - 0.5

    tform_ds = skimage.transform.AffineTransform()
    tform_ds.estimate(src_corners, dst_corners)
    if do_shift:
        if subpixel_shift: 
            # if this is true, we add an additional 'arbitrary' subpixel shift, which 'aligns'
            # the grid of the target image with the original image in such a way that the interpolation
            # is 'cleaner', i.e. groups of <ds_factor> pixels in the original image will map to
            # individual pixels in the resulting image.
            #
            # without this additional shift, and when the downsampling factor does not divide the image
            # size (like in the case of 424 and 3.0 for example), the grids will not be aligned, resulting
            # in 'smoother' looking images that lose more high frequency information.
            #
            # technically this additional shift is not 'correct' (we're not looking at the very center
            # of the image anymore), but it's always less than a pixel so it's not a big deal.
            #
            # in practice, we implement the subpixel shift by rounding down the orig_size to the
            # nearest multiple of the ds_factor. Of course, this only makes sense if the ds_factor
            # is an integer.

            cols = (cols // int(ds_factor)) * int(ds_factor)
            rows = (rows // int(ds_factor)) * int(ds_factor)
            # print "NEW ROWS, COLS: (%d,%d)" % (rows, cols)


        shift_x = cols / (2 * ds_factor) - tcols / 2.0
        shift_y = rows / (2 * ds_factor) - trows / 2.0
        tform_shift_ds = skimage.transform.SimilarityTransform(translation=(shift_x, shift_y))
        return tform_shift_ds + tform_ds
    else:
        return tform_ds

    return tform_ds

def build_augmentation_transform(orig_size, zoom=1.0, rotation=0, shear=0, translation=(0, 0)):
    center_shift = np.array(orig_size) / 2. - 0.5
    tform_center = skimage.transform.SimilarityTransform(translation=-center_shift)
    tform_uncenter = skimage.transform.SimilarityTransform(translation=center_shift)

    tform_augment = skimage.transform.AffineTransform(scale=(1/zoom, 1/zoom), rotation=np.deg2rad(rotation), shear=np.deg2rad(shear), translation=translation)
    tform = tform_center + tform_augment + tform_uncenter # shift to center, augment, shift back (for the rotation/shearing)
    return tform

def random_perturbation_transform(orig_size, zoom_range, rotation_range, shear_range, translation_range, do_flip=False):
    # random shift [-4, 4] - shift no longer needs to be integer!
    shift_x = np.random.uniform(*translation_range)
    shift_y = np.random.uniform(*translation_range)
    translation = (shift_x, shift_y)

    # random rotation [0, 360]
    rotation = np.random.uniform(*rotation_range) # there is no post-augmentation, so full rotations here!

    # random shear [0, 5]
    shear = np.random.uniform(*shear_range)

    # # flip
    if do_flip and (np.random.randint(2) > 0): # flip half of the time
        shear += 180
        rotation += 180
        # shear by 180 degrees is equivalent to rotation by 180 degrees + flip.
        # So after that we rotate it another 180 degrees to get just the flip.

    # random zoom [0.9, 1.1]
    # zoom = np.random.uniform(*zoom_range)
    log_zoom_range = [np.log(z) for z in zoom_range]
    zoom = np.exp(np.random.uniform(*log_zoom_range)) # for a zoom factor this sampling approach makes more sense.
    # the range should be multiplicatively symmetric, so [1/1.1, 1.1] instead of [0.9, 1.1] makes more sense.

    return build_augmentation_transform(orig_size, zoom, rotation, shear, translation)

def perturb_and_dscrop(img, ds_transforms, augmentation_params, orig_size=None, target_sizes=None):
    if target_sizes is None: # default to (53,53) for backwards compatibility
        target_sizes = [(48, 48) for _ in xrange(len(ds_transforms))]

    tform_augment = random_perturbation_transform(orig_size,**augmentation_params)
    # return [skimage.transform.warp(img, tform_ds + tform_augment, output_shape=target_size, mode='reflect').astype('float32') for tform_ds in ds_transforms]

    result = []
    for tform_ds, target_size in zip(ds_transforms, target_sizes):
#         result.append(fast_warp(img, tform_ds + tform_augment, output_shape=target_size, mode='reflect').astype('float32'))
          result.append(warp(img,tform_ds+tform_augment, output_shape=target_size,mode='reflect'))

    return result

def load_and_process_images(folder):
    i=0
    for fileNameDir in os.walk(folder):   
        for fileName in fileNameDir[2]:
            i+=1
            imgf = "{0}{1}{2}".format(fileNameDir[0], os.sep, fileName)  
            img = imread(imgf)

            row,col=img.shape
            tform_ds_8x = build_ds_transform(8.0, orig_size=(row,col), target_size=target_size, do_shift=True, subpixel_shift=False)
            tform_ds_cropped33 = build_ds_transform(3.0, orig_size=(row,col), target_size=target_size, do_shift=True, subpixel_shift=False)
            tform_ds=[tform_ds_cropped33, tform_ds_8x]

            target_sizes=[target_size for _ in xrange(len(tform_ds))]

            spimgf = imgf.split('/')
            # image_path = '/'.join(spimgf[:-1])
            image_path=fo+spimgf[:-1][-1]
            # print image_path
            image_file = spimgf[-1].split('.')[0]
     
            aug_imgs = perturb_and_dscrop(img,tform_ds,default_augmentation_params, orig_size=(row,col), target_sizes=target_sizes)

            for i,aug_img in enumerate(aug_imgs):
                imsave(image_path + '/' + image_file + '_aug' + str(i+1) + '.jpg',aug_img)

def master_joblib_loop():
    Parallel(n_jobs=-1)(delayed(load_and_process_images)(folder) for i,folder in enumerate(directory_names))

def delete_files(filenm):
    cmd='rm -f {}'.format(filenm)
    # print cmd
    return os.system(cmd)

def delete_joblib_loop():
    Parallel(n_jobs=-1)(delayed(delete_files)(filenm) for filenm in orig_images)


if len(sys.argv) < 3:
    print sys.argv
    print "Usage: python realaug.py input_folder output_folder resolution(l/w)"
    exit(1)

fi = sys.argv[1]
fo = sys.argv[2]
length=width=int(sys.argv[3])
target_size=(length,width)
directory_names = list(set(glob.glob(os.path.join(fi, "*")) ).difference(set(glob.glob(os.path.join(fi,"*.*")))))

if fi==fo:
    print "Resizing Input - skipping image copy"
else:
    print "Copying Directory Tree from %s to %s" %(fi,fo)
    # cmd="find {} -type d -exec mkdir -- {}".format(fi,fo)+"{} \;"
    cmd='''rsync -a -f"+ */" -f"- *" {} {}'''.format(fi,fo)
    print "Executing %s" %cmd
    os.system(cmd)

    # print "Copying Images from %s to %s" %(fi,fo)
    # cmd="cp -r {}* {}".format(fi, fo)
    # print "Executing %s" %cmd
    # #os.system(cmd)

# print directory_names
master_joblib_loop()

# orig_images=list(set(glob.glob(os.path.join(fo+"*/", "*"))).difference(set(glob.glob(os.path.join(fo+"*/", "*_*")))))
# delete_joblib_loop()

# Append the string class name for each class

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

