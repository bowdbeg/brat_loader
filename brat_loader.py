import os
import pickle as pkl
from abc import ABCMeta
from abc import abstractmethod


class BaseAnnData(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    def tag(self):
        return self._tag

    @property
    def label(self):
        return self._label


class Entity(BaseAnnData):
    def __init__(self, tag, label, start, end, entity):
        self._tag = tag
        self._label = label
        self._start = start
        self._end = end
        self._entity = entity

    def __str__(self):
        return self.entity

    def __repr__(self):
        return self.entity

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def entity(self):
        return self._entity


class Relation(BaseAnnData):
    def __init__(self, tag, label, arg1, arg2):
        self._tag = tag
        self._label = label
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg1_ref = ''
        self._arg2_ref = ''

    def set_reference(self, arg1, arg2):
        self._arg1_ref = arg1
        self._arg2_ref = arg2

    @property
    def arg1(self):
        return self._arg1_ref

    @property
    def arg2(self):
        return self._arg2_ref


# data structure for text data and annotation data
class TextData():
    def __init__(self, text_file, ann_file):
        self._text_file = os.path.abspath(text_file)
        self._ann_file = os.path.abspath(ann_file)
        self._data = {}
        self._raw_text = ''
        self._raw_ann = ''

        # load files
        with open(self._text_file) as f:
            self._raw_text = f.read()
        with open(self._ann_file) as f:
            self._raw_ann = f.read()

    def parse_ann(self):
        lines = self._raw_ann.strip().split('\n')
        syn_num = 1

        for line in lines:
            line_sp = line.split('\t')
            tag = line_sp[0]
            assert not (tag in self._data.keys()), 'Tag is overlapped.'
            if 'T' in tag:
                # entity
                tmp = line_sp[1].split()
                label = tmp[0]
                start = tmp[1]
                end = tmp[2]
                entity = line_sp[2]
                self._data[tag] = Entity(tag, label, start, end, entity)
            else:
                assert tag in '*' or tag in 'R', 'tag oversight ({})'.format(
                    tag)
                d = line_sp.split()
                label = d[0]
                if tag in '*':
                    # tag assign uniquely
                    tag = 'S{}'.format(syn_num)
                    syn_num += 1
                    arg1 = d[1]
                    arg2 = d[2]
                else:
                    arg1 = d[1][5:]
                    arg2 = d[2][5:]
                self._data[tag] = Relation(tag, label, arg1, arg2)

        # set reference to Relation instance
        for tag in self._data.keys():
            if tag in 'R' or tag in '*':
                # relation
                self._data[tag].set_reference(self._data[self._data[tag].arg1],
                                              self._data[self._data[tag].arg2])
            else:
                # entity
                pass

    @property
    def tags(self):
        return self._data.keys()

    @property
    def text(self):
        return self._raw_text

    @property
    def data(self):
        return self._data



# dataset of texts (have list of TextData)
class TextDataset():
    def __init__(self):
        self._data = {}

    def read(self, file_list):
        # files is list of tuple
        # [(hoge.txt, hoge.ann), (fuga.txt, fuga.ann)]
        for files in file_list:
            name = files[0].split('.')[0]
            dat = TextData(files[0], files[1])
            if name in self._data.keys():
                raise ValueError('File names have to be unique.')
            self._data[name] = dat

    @property
    def keys(self):
        return self._data.keys

    @property
    def data(self):
        return self._data

    def save(self, file):
        with open(file, 'wb') as f:
            pkl.dump(self._data, f)

    def load(self, file):
        with open(file, 'rb') as f:
            self._data = pkl.load(f)








if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('mode', type=str)
    # parser.add_argument(
    #     '--sp_args',
    #     type=str,
    #     required=False,
    #     default=
    #     '--input=scienceie/train_data.txt,--model_prefix=sp_model,--vocab_size=32000,--character_converage=1.0,--model_type=unigram',
    #     help='argument for sentencepiece training')

    # args = parser.parse_args()
    from glob import glob

    files = glob('scienceie/test/*')
    file_list = []
    for file in files:
        if '.txt' in file:
            file_list.append((file, file[:-4] + '.ann'))
    dataset = TextDataset()
    dataset.read(file_list)
    print(dataset.data)
    dataset.save('test.dataset')
