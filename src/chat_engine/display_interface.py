from abc import ABC, abstractmethod

class DisplayInterface(ABC):

    @abstractmethod
    async def info(self, message: str):
        raise NotImplementedError

    @abstractmethod
    async def warn(self, message: str):
        raise NotImplementedError

    @abstractmethod
    async def error(self, message: str):
        raise NotImplementedError

    @abstractmethod
    async def markdown(self, prompt: str) -> str:
        raise NotImplementedError
