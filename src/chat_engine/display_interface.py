from abc import ABC, abstractmethod

class DisplayInterface(ABC):

    @abstractmethod
    def info(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def warn(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def markdown(self, prompt: str) -> str:
        raise NotImplementedError
