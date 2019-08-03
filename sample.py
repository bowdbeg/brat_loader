import brat_loader as bl
from glob import glob


data = bl.TextDataset()

file_list = []
files = glob('data/*.txt')
for file in files:
    ann = file[:-4] + '.ann'
    file_list.append((file, ann))

data.read(file_list)
data.save('test.dat')


del data

data=bl.TextDataset()
data.load('sample.dat')

for key in data.keys():
    print(data[key].tags())