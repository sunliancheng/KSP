from abc import ABC

from dev.Logger.GenericLogger import GenericLogger


class MetaClass(ABC):
    def __init__(self):
        self.logger = GenericLogger()
