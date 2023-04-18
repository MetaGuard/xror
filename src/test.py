from xror import XROR
from pprint import pprint
import os
from deepdiff import DeepDiff
import numpy as np
from bsor.Bsor import make_bsor

with open('sample.bsor', 'rb') as f:
    first = XROR.fromBSOR(f, addFPS = True)

data = first.pack()
a = os.path.getsize('sample.bsor')
b = len(data)
print(a, '->', b, '(' + str(round(b/a,4)*100) + '%)')

with open('sample.xror', 'wb') as f:
    f.write(data)

with open('sample.xror', 'rb') as f:
    file = f.read()

second = XROR.unpack(file)

diff = DeepDiff(first.data, second.data)
print('Lossless', np.array_equal(first.data['frames'], second.data['frames']), '(Changes:', diff, ')')

output = second.toBSOR()
with open('output.bsor', 'wb') as f:
    f.write(output)

with open('sample.bsor', 'rb') as f:
    a = f.read()
with open('output.bsor', 'rb') as f:
    b = f.read()

print('Identical', a == b)
