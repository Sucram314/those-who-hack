import pickle as pk
import numpy as np
from model import Aimer
from PIL import Image

with open(r"C:\Users\marcu\OneDrive\Documents\GitHub\those-who-hack\src\data\aimer.pk","rb") as f:
    obj : Aimer = pk.load(f)

num = 50

a = obj.data.input.T[num]
a = np.reshape(a,(20,20))

img = Image.fromarray(np.uint8(a * 255), 'L')
img.show()

out = obj.data.output.T[num]
print(list(out))

print(obj.data.labels[num])
