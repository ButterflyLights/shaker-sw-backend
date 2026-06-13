import struct
import numpy as np

def writeFile(filename, arr):
    arr = np.array(arr).astype(np.float64)
    with open(filename, 'wb+') as f:
        f.write(struct.pack("<Q", arr.size))
        arr.tofile(f)

def readFile(filename):
    with open(filename, 'rb') as f:
        count = struct.unpack("<Q", f.read(8))[0]
        arr = np.fromfile(f, dtype=np.float64, count=count)

    return arr

if __name__ == "__main__":
    # writeFile("../data/test/test.bin", np.array([1, 2, 3, 4, 5]))
    print(readFile("../data/test/test.bin"))