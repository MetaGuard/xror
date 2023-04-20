import sys
import os
from deepdiff import DeepDiff
dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
os.chdir(dir)

from src.xror import XROR
import numpy as np

def test_bsor():
    with open('./data/bsor/sample1.bsor', 'rb') as f:
        first = XROR.fromBSOR(f, addFPS = True)

    data = first.pack()

    with open('./data/bsor/sample1.xror', 'wb') as f:
        f.write(data)

    with open('./data/bsor/sample1.xror', 'rb') as f:
        file = f.read()

    second = XROR.unpack(file)
    assert np.array_equal(first.data['frames'], second.data['frames'])

    diff = DeepDiff(first.data, second.data)
    assert diff == {}

    output = second.toBSOR()
    with open('./data/bsor/output1.bsor', 'wb') as f:
        f.write(output)

    with open('./data/bsor/sample1.bsor', 'rb') as f:
        a = f.read()
    with open('./data/bsor/output1.bsor', 'rb') as f:
        b = f.read()

    assert a == b
