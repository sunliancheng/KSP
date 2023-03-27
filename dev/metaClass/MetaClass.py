from abc import ABC

from dev.logger.GenericLogger import GenericLogger


class MetaClass(ABC):
    def __init__(self):
        self.logger = GenericLogger()
