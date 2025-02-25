import traceback
from datetime import datetime


loggers = {}


def get_logger(name):
    if name not in loggers:
        loggers[name] = PrintLogger()

    return loggers[name]


def set_logger(name, logger):
    loggers[name] = logger


class PrintLogger(object):
    """
    Implementation of weblogger that only prints to std out
    """

    def info(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        if stack:
            stack_lines = traceback.format_stack()
            stack_string = "".join(stack_lines)
            print("Stack:")
            print("".join(stack_lines))

    def debug(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        if stack:
            stack_lines = traceback.format_stack()
            stack_string = "".join(stack_lines)
            print("Stack:")
            print("".join(stack_lines))

    def warning(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        if stack:
            stack_lines = traceback.format_stack()
            stack_string = "".join(stack_lines)
            print("Stack:")
            print("".join(stack_lines))

    def error(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        if stack:
            stack_lines = traceback.format_stack()
            stack_string = "".join(stack_lines)
            print("Stack:")
            print("".join(stack_lines))

    def notify(self, info_text, detail_text="", user=None):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

    def exc(self, exception_object, info_text=None, user=None):
        if exception_object:
            print(str(exception_object))

        error_text = traceback.format_exc()
        print("Exception format")
        print(error_text)

        stack_lines = traceback.format_stack()
        stack_string = "".join(stack_lines)
        print("Stack:")
        print("".join(stack_lines))


class PermanentLogger(object):
    """
    Implementation of weblogger that only prints to std out
    """

    def __init__(self):
        self.permanent_data = []

    def info(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        if len(self.permanent_data) > 200:
            self.permanent_data.pop(0)

        self.add(("INFO", datetime.now(), info_text, detail_text, user))

    def debug(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        if len(self.permanent_data) > 200:
            self.permanent_data.pop(0)

        self.add(("DEBUG", datetime.now(), info_text, detail_text, user))

    def warning(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        self.add(("WARNING", datetime.now(), info_text, detail_text, user))

    def error(self, info_text, detail_text="", user=None, stack=False):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        self.add(("ERROR", datetime.now(), info_text, detail_text, user))

    def notify(self, info_text, detail_text="", user=None):
        if info_text:
            print(info_text)
        if detail_text:
            print(detail_text)

        self.add(("NOTIFY", datetime.now(), info_text, detail_text, user))

    def exc(self, exception_object, info_text=None, user=None):
        if exception_object:
            print(str(exception_object))

        error_text = traceback.format_exc()
        print("Exception format")
        print(error_text)

        stack_lines = traceback.format_stack()
        stack_string = "".join(stack_lines)
        print("Stack:")
        print(stack_string)

        info_text = info_text + "\n" + str(exception_object)

        detail_text = error_text + "\n" + stack_string

        self.add(("EXC", datetime.now(), info_text, detail_text, user))

    def add(self, data):
        if len(self.permanent_data) > 200:
            self.permanent_data.pop(0)

        self.permanent_data.append(data)
