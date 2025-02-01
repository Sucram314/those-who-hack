from abc import ABC, abstractmethod

class Enemy(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass