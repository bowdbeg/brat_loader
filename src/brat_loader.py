import os
import pickle as pkl
from abc import ABCMeta
from abc import abstractmethod


class BaseAnnData(metaclass=ABCMeta):
    """
    Abstruct class for annotation data such as Entity and Relation.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    def tag(self):
        """
        Getter of tag such as T1 and R2.
        """

        return self._tag

    @property
    def label(self):
        """
        Getter of label such as Location and Location-of.
        """

        return self._label


class Entity(BaseAnnData):
    """
    Entity class for saving attributes.
    Normally, do not use this class directly.
    
    Attributes
    ----------
    tag : str
        Tag of Entity such as \"T1\".
    label : str
        Label of Entity such as \"Location\", \"Material\" and so on.
    start : int
    end : int
        Entity starts from \"start\" to \"end\" (word count).
    entity : str
        Entity phrase.
    """

    def __init__(self, tag, label, start, end, entity):
        """
        Constructor.

        Parameters
        ----------
        tag : str
            Tag of Entity such as \"T1\".
        label : str
            Label of Entity such as \"Location\", \"Material\" and so on.
        start : int
        end : int
            Entity is from \"start\" to \"end\" (word count).
        entity : str
            Entity phrase.
        """

        self._tag = tag
        self._label = label
        self._start = start
        self._end = end
        self._entity = entity

    def __str__(self):
        return self._entity

    @property
    def start(self):
        """
        Getter of entity start.

        Returns
        -------
        start : int
            Entity start.
        """

        return self._start

    @property
    def end(self):
        """
        Getter of entity end.

        Returns
        -------
        end : int
            Entity end.
        """

        return self._end

    @property
    def entity(self):
        """
        Getter of entity phrase.

        Returns
        -------
        entity : str
            Entity phrase.
        """

        return self._entity


class Relation(BaseAnnData):
    """
    Relation class for saving attributes.
    Normally, do not use this class directly.
    
    Attributes
    ----------
    tag : str
        Tag of entity such as \"R1\".
    label : str
        Label of entity such as \"Location-of\", \"Process-of\" and so on.
    arg1 : Entity
        arg1 of relation.
    arg2 : Entity
        arg2 of relation.
    """

    def __init__(self, tag, label, arg1, arg2):
        """
        Constructor.
        
        Attributes
        ----------
        tag : str
            Tag of entity such as \"R1\".
        label : str
            Label of entity such as \"Location-of\", \"Process-of\" and so on.
        arg1 : Entity
            arg1 tag of relation.
        arg2 : Entity
            arg2 tag of relation.
        """

        self._tag = tag
        self._label = label
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg1_ref = ''
        self._arg2_ref = ''

    def _set_reference(self, arg1, arg2):
        """
        Setter to set reference to arg1 and arg2 entity.

        Parameters
        ----------
        arg1 : Entity
            Reference to arg1 entity.
        arg2 : Entity
            Referemce to arg2 entity.
        """

        self._arg1_ref = arg1
        self._arg2_ref = arg2

    def __str__(self):
        return self._label

    @property
    def arg1(self):
        """
        Getter of arg1 reference.

        Returns
        -------
        arg1 : Entity
            Reference to arg1 entity.
        """

        return self._arg1_ref

    @property
    def arg2(self):
        """
        Getter of arg2 reference.

        Returns
        -------
        arg2 : Entity
            Reference to arg2 entity.
        """

        return self._arg2_ref


# data structure for text data and annotation data
class Document():
    """
    Class to save attribute of document.
    Normally, do not use this class directly.

    Attributes
    ----------
    text_file : str
        Path to text file.
    ann_file : str
        Path to annotation file.
    data : dict
        Dictionary of tags (key: \"T1\",\"R1\"...).
        Do not access directlly
    text : str
        Raw text data.
    """

    def __init__(self, text_file, ann_file):
        """
        Constructor.

        Parameters
        ----------
        text_file : str
            Path to text file.
        ann_file : str
            Path to annotation file.
        """

        self._text_file = os.path.abspath(text_file)
        self._ann_file = os.path.abspath(ann_file)
        self._data = {}
        self._raw_text = ''
        self._raw_ann = ''

        if not os.path.exists(self.text_file):
            raise ValueError('Path {} do not exist.'.format(text_file))
        if not (os.path.exists(self.ann_file)):
            raise ValueError('Path {} do not exitst.'.format(ann_file))

        # load files
        with open(self._text_file) as f:
            self._raw_text = f.read()
        with open(self._ann_file) as f:
            self._raw_ann = f.read()

        self._parse_ann()

    def _parse_ann(self):
        """
        Parse annotation file.
        """

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
            if 'R' in tag or 'S' in tag:
                # relation
                self._data[tag]._set_reference(
                    self._data[self._data[tag]._arg1],
                    self._data[self._data[tag]._arg2])
            else:
                # entity
                pass

    def tags(self):
        """
        Get tags (\"T1\",\"R1\"...) of annotation as dict_key.
        
        Returns
        -------
        tags : dict_keys
            Tags (\"T1\",\"R1\"...) of annotation.
        """

        return self._data.keys()

    @property
    def text(self):
        """
        Getter for raw text.

        Returns
        -------
        raw_text : str
            Raw text of document.
        """

        return self._raw_text

    @property
    def text_file(self):
        """
        Getter for path to text file.

        Returns
        -------
        text_file : str
            Path to text file.
        """

        return self._text_file

    @property
    def ann_file(self):
        """
        Getter for path to annotation file.

        Returns
        -------
        ann_file : str
            Path to annotaiton file.
        """

        return self._ann_file

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


class TextDataset():
    """
    Dataset of brat documents.

    Attributes
    ----------
    data : dict
        Dictionary of Document.
    """

    def __init__(self):
        """
        Constructor.
        """

        self._data = {}

    def read(self, file_list):
        """
        Read files.

        Parameters
        ----------
        file_list : list
            File list to read.
            Elements must be tuple.
            [(hoge.txt,fuga.ann)...]
        """

        for files in file_list:
            self.read(files[0], files[1])

    def read(self, text_file, ann_file):
        """
        Read one file.

        Parameters
        ----------
        text_file : str
            Path to text file.
        ann_file : str
            Path to annotation file.
        """

        text_file = os.path.abspath(text_file)
        ann_file = os.path.abspath(ann_file)
        # remove extention
        name = '.'.join(text_file[0].split('.')[:-1])
        dat = Document(text_file, ann_file)
        if name in self._data.keys():
            raise ValueError('File names have to be unique.')
        self._data[name] = dat

    def keys(self):
        """
        Get documents key.

        Returns
        -------
        keys : dict_keys
            Key of Document.
        """

        return self._data.keys()

    def tags(self, key):
        """
        Get tags of document.

        Parameters
        ----------
        key : str
            Key of Document.

        Returns
        -------
        tags : dict_keys
            Tags of annotation data.
        """

        return self._data[key].tags()

    def save(self, file):
        """
        Save dataset.

        Parameters
        ----------
        file : str
            Path to save.
        """

        with open(file, 'wb') as f:
            pkl.dump(self._data, f)

    def load(self, file):
        """
        Load dataset.

        Parameters
        ----------
        file : str
            Dataset path to load.
        """

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