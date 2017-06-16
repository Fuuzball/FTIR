import spectral.io.envi as envi
import matplotlib.pyplot as plt
import numpy as np

lib = envi.open('./data/test.hdr')
spec = np.array(lib[:,:,:])
spec = np.flipud(spec)
#spec[np.isnan(spec)] = 0
print(spec.shape)
plt.imshow(spec[:,:,0], cmap = 'gray')
plt.show()
