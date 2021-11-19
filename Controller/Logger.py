enable_colors = True


class Logger:
    __PINK = '\033[95m'
    __BLUE = '\033[94m'
    __CYAN = '\033[96m'
    __GREEN = '\033[92m'
    __YELLOW = '\033[93m'
    __RED = '\033[91m'
    __ENDC = '\033[0m'
    __UNDERLINE = '\033[4m'

    def __colored(self, content: str, color: str):
        if enable_colors:
            print(f"{color}{content}{self.__ENDC}")
        else:
            print(content)

    def info(self, content: str):
        self.__colored(content, self.__BLUE)

    def success(self, content: str):
        self.__colored(content, self.__CYAN)

    def warn(self, content: str):
        self.__colored(content, self.__YELLOW)

    def log(self, content: str):
        self.__colored(content, self.__GREEN)

    def error(self, content: str):
        self.__colored(content, self.__RED)


logger = Logger()


if __name__ == "__main__":
    colors = ['\033[95m', '\033[94m', '\033[96m', '\033[92m',
              '\033[93m', '\033[91m']

    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    print()
    for i, color in enumerate(colors):
        print(f'{color}{str(i).zfill(2)} default style{ENDC}')
        print(f'{color}{UNDERLINE}{str(i).zfill(2)} underline style{ENDC}\n')
