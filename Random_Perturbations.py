
# coding: utf-8

# In[33]:

from skimage.io import imread
import matplotlib.pyplot as plt
from pylab import cm
from skimage.transform import AffineTransform, SimilarityTransform, warp, resize
import numpy as np


# In[226]:

img=imread('//home/shankarmsy/Documents/DataSci/git_home/Public/kaggle_Data_Science_Bowl/train/chaetognath_sagitta/100929.jpg',as_grey=True)
plt.imshow(img,cmap=cm.gray)
plt.show()


# In[103]:

img_r=resize(img,(48,48))
plt.imshow(img_r,cmap=cm.gray)


# In[75]:

def build_ds_transform(ds_factor=1.0, orig_size=(424, 424), target_size=(53, 53), do_shift=True, subpixel_shift=False):
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
    return tform_ds


# In[117]:

default_augmentation_params = {
    'zoom_range': (1.0, 1.1),
    'rotation_range': (0, 360),
    'shear_range': (0, 0),
    'translation_range': (-4, 4),
}


# In[148]:

def random_perturbation_transform(zoom_range, rotation_range, shear_range, translation_range, do_flip=False):
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

    print zoom, rotation, shear, translation
    return build_augmentation_transform(zoom, rotation, shear, translation)


# In[146]:

def perturb_and_dscrop(img, ds_transforms, augmentation_params, target_sizes=None):
    if target_sizes is None: # default to (53,53) for backwards compatibility
        target_sizes = [(53, 53) for _ in xrange(len(ds_transforms))]

    tform_augment = random_perturbation_transform(**augmentation_params)
    # return [skimage.transform.warp(img, tform_ds + tform_augment, output_shape=target_size, mode='reflect').astype('float32') for tform_ds in ds_transforms]

    result = []
    for tform_ds, target_size in zip(ds_transforms, target_sizes):
#         result.append(fast_warp(img, tform_ds + tform_augment, output_shape=target_size, mode='reflect').astype('float32'))
          new=warp(img,tform_ds+tform_augment, output_shape=target_size,mode='reflect')
          result.append(new)
          plt.imshow(new,cmap=cm.gray)

    return result


# In[136]:

center_shift = np.array((row, col)) / 2. - 0.5
tform_center = skimage.transform.SimilarityTransform(translation=-center_shift)
tform_uncenter = skimage.transform.SimilarityTransform(translation=center_shift)

def build_augmentation_transform(zoom=1.0, rotation=0, shear=0, translation=(0, 0)):
    tform_augment = skimage.transform.AffineTransform(scale=(1/zoom, 1/zoom), rotation=np.deg2rad(rotation), shear=np.deg2rad(shear), translation=translation)
    tform = tform_center + tform_augment + tform_uncenter # shift to center, augment, shift back (for the rotation/shearing)
    return tform


# In[137]:

def load_and_process_image(img, ds_transforms, augmentation_params, target_sizes=None):
    # start_time = time.time()
#     img_id = load_data.train_ids[img_index]
#     img = load_data.load_image(img_id, from_ram=True)
    # load_time = (time.time() - start_time) * 1000
    # start_time = time.time()
    img_a = perturb_and_dscrop(img, ds_transforms, augmentation_params, target_sizes)
    # augment_time = (time.time() - start_time) * 1000
    # print "load: %.2f ms\taugment: %.2f ms" % (load_time, augment_time)
    return img_a


# In[212]:

row,col=img.shape
tform_ds_8x = build_ds_transform(8.0, orig_size=(row,col), target_size=(48, 48))
tform_ds_cropped33 = build_ds_transform(3.0, orig_size=(row,col), target_size=(48, 48))
tform_ds=[tform_ds_cropped33, tform_ds_8x]


# In[234]:

img_new=perturb_and_dscrop(img,tform_ds,default_augmentation_params)


# In[235]:

fig=plt.figure(figsize=(8,8)) 
for i in range(len(img_new)): 
    ax=fig.add_subplot(1,2,i+1,xticks=[], yticks=[]) 
    ax.imshow(img_new[i], cmap=cm.gray) 
plt.show()


# In[224]:

len(img_new)


# In[ ]:



