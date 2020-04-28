"""Utils for a more beautiful CMD interface"""
import os


class bcolors:
    HEADER = '\033[1;97m'
    INFO = '\033[1;97m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


rows, columns = os.popen('stty size', 'r').read().split()
columns = int(columns)


def print_separator(symbol, text, colour=None):
    left = int((columns - len(text) - 2) / 2)
    right = columns - left - len(text) - 2
    if colour:
        print(f"{colour}", end='')
    print(symbol * left, text, symbol * right)
    if colour:
        print(f"{bcolors.ENDC}", end='')


def print_line(text, status=None):
    if status == 'fail':
        colour = bcolors.FAIL
    elif status == 'success':
        colour = bcolors.OKGREEN
    else:
        colour = bcolors.INFO
    print_separator('=', text, colour)


def print_info(text, **args):
    print(f"{bcolors.INFO}{text}{bcolors.ENDC}", **args)


def print_success(text, **args):
    print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}")


def print_fail(text, exception):
    print(f"{bcolors.FAIL}{text}{bcolors.ENDC}", exception)
