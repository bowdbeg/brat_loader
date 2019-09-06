from .. import brat_loader
import scispacy
import spacy

# TODO: scentencepiece


class TextProcessor():
    def __init__(self, dataset):
        self.dataset = dataset

    def __call__(self):
        self.process()

    def process(self):
        # forward all processes
        pass

    def sent2piece(self, text):
        pass

    def load_ann(self, ann_fname):
        pass

    def load_text(self):
        pass
