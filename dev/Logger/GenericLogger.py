import string
from datetime import datetime


class GenericLogger:
    def __init__(self):
        self.common_prefix = " | "
        self.common_suffix = " "

    def info(self, str: string):
        log = 'INFO | ' + self.get_current_time() + self.common_prefix + str + self.common_suffix
        self.console_print(log)

    def debug(self, str: string):
        log = 'DEBUG | ' + self.get_current_time() + self.common_prefix + str + self.common_suffix
        self.console_print(log)

    def error(self, str: string):
        log = 'ERROR | ' + self.get_current_time() + self.common_prefix + str + self.common_suffix
        self.console_print(log)

    def warn(self, str: string):
        log = 'WARN | ' + self.get_current_time() + self.common_prefix + str + self.common_suffix
        self.console_print(log)

    def get_current_time(self) -> string:
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def console_print(self, str: string):
        print(str)
