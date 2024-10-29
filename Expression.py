from abc import ABC, abstractmethod

class Expression(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def equals(self, other: 'Expression') -> bool:
        pass
