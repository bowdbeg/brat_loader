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

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def entity(self):
        return self._entity

    @property
    def label(self):
        return self._label


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

    def __str__(self):
        return self._label

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

        self.parse_ann()

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
                assert '*' in tag or 'R' in tag, 'tag oversight ({})'.format(
                    tag)
                d = line_sp[1].split()
                label = d[0]
                if '*' in tag:
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
            if 'R' in tag or '*' in tag:
                # relation
                self._data[tag].set_reference(
                    self._data[self._data[tag]._arg1],
                    self._data[self._data[tag]._arg2])
            else:
                # entity
                pass

    def tags(self):
        return self._data.keys()

    @property
    def text(self):
        return self._raw_text

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self._data.keys())

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, p):
        return p in self._data.keys()


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

    def keys(self):
        return self._data.keys()

    def tags(self, key):
        return self._data[key].tags()

    def save(self, file):
        with open(file, 'wb') as f:
            pkl.dump(self._data, f)

    def load(self, file):
        with open(file, 'rb') as f:
            self._data = pkl.load(f)

    def __len__(self):
        return len(self._data.keys())

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, p):
        return p in self._data.keys()

    def __call__(self, file_list):
        self.read(file_list)