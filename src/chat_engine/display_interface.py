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

    @abstractmethod
    async def quit(self, message: str = None):
        raise NotImplementedError

    @abstractmethod
    async def ask_yes_no(self, question: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def ask_question(self, question: str) -> str:
        raise NotImplementedError

    async def tool_log(self, message: str):
        return False
    
