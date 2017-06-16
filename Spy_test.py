import spectral.io.envi as envi
import matplotlib.pyplot as plt
from sklearn import svm
import numpy as np

lib = envi.open('./data/test.hdr')
spec = np.array(lib[:,:,:])
spec = np.flipud(spec)

print(spec.shape)
plt.imshow(spec[:,:,0], cmap = 'gray')
plt.show()
