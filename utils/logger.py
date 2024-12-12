import traceback


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
        print(info_text)
        if detail_text:
            print(detail_text)

    def debug(self, info_text, detail_text="", user=None, stack=False):
        print(info_text)
        if detail_text:
            print(detail_text)

    def warning(self, info_text, detail_text="", user=None, stack=False):
        print(info_text)
        if detail_text:
            print(detail_text)

    def error(self, info_text, detail_text="", user=None, stack=False):
        print(info_text)
        if detail_text:
            print(detail_text)

    def notify(self, info_text, detail_text="", user=None):
        print(info_text)
        if detail_text:
            print(detail_text)

    def exc(self, exception_object, info_text=None, user=None):
        print(str(exception_object))

        error_text = traceback.format_exc()
        print("Exception format")
        print(error_text)

        stack_lines = traceback.format_stack()
        stack_string = "".join(stack_lines)
        print("Stack:")
        print("".join(stack_lines))
