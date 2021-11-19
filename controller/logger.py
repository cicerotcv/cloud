from typing import Literal


class Colors:
    __PINK = '\033[95m'
    __BLUE = '\033[94m'
    __CYAN = '\033[96m'
    __GREEN = '\033[92m'
    __YELLOW = '\033[93m'
    __RED = '\033[91m'
    __UNDERLINE = '\033[4m'
    __ENDC = '\033[0m'

    def __apply_color(self, content: str, color: Literal):
        return f"{color}{content}{self.__ENDC}"

    def pink(self, content: str):
        return self.__apply_color(content, self.__PINK)

    def blue(self, content: str):
        return self.__apply_color(content, self.__BLUE)

    def cyan(self, content: str):
        return self.__apply_color(content, self.__CYAN)

    def green(self, content: str):
        return self.__apply_color(content, self.__GREEN)

    def yellow(self, content: str):
        return self.__apply_color(content, self.__YELLOW)

    def red(self, content: str):
        return self.__apply_color(content, self.__RED)

    def underline(self, content: str):
        return self.__apply_color(content, self.__UNDERLINE)


class Logger:
    def __init__(self, enable_colors=True):
        self.__colors = Colors()
        if enable_colors:
            self.__print_function__ = lambda content, apply_color: print(
                apply_color(content))
        else:
            self.__print_function__ = lambda content, apply_color: print(
                content)

    def info(self, content: str):  # blue
        self.__print_function__(content, self.__colors.blue)

    def success(self, content: str):  # cyan
        self.__print_function__(content, self.__colors.cyan)

    def warn(self, content: str):  # yellow
        self.__print_function__(content, self.__colors.yellow)

    def log(self, content: str):  # green
        self.__print_function__(content, self.__colors.green)

    def error(self, content: str):  # red
        self.__print_function__(content, self.__colors.red)
