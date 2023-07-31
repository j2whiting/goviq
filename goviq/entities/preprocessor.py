from abc import ABC, abstractmethod


class Preprocessor(ABC):
    _version = 1
    cache_path = None

    @abstractmethod
    def load(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def cache(self, **kwargs):
        raise NotImplementedError()
