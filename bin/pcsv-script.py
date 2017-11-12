#! /usr/bin/env python3

import sys
from argparse import ArgumentParser

from pcsv import Pcsv


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('cmd', help='command name', choices=Pcsv.COMMANDS)
    parser.add_argument('-d', '--delimiter', help='delimiter', default=',')
    parser.add_argument('-l', '--limit', help='limit', type=int)
    parser.add_argument('-f', '--fields', help='fields')
    parser.add_argument('-c', '--cond', help='condition')
    parser.add_argument('-e', '--extract', help='extract')
    parser.add_argument('-k', '--key', help='key', default='0')
    parser.add_argument('-b', '--begin', help='begin', default='0')
    parser.add_argument('-r', '--reduce', help='reduce')
    parser.add_argument('--head', help='head', action='store_true')

    args = parser.parse_args()

    Pcsv(args).pipe(sys.stdin, sys.stdout)
