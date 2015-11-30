#! /usr/bin/env python

import re
import sys
import csv
import math
import errno
from argparse import ArgumentParser



def _convert(e):
    try:
        return eval(e)
    except Exception:
        return e


def count(args):
    """
        cat example.csv | pcsv count
    """
    c = -1
    for _ in sys.stdin:
        c += 1
    print >> sys.stdout, c
    sys.stdout.flush()


def limit(args):
    """
        cat example.csv | pcsv limit -l 10
    """
    c = -1
    for line in sys.stdin:
        sys.stdout.write(line)
        sys.stdout.flush()
        c += 1
        if c >= args.limit:
            break


def select(args):
    """
        cat example.csv | pcsv select -f 'field1 field2'
    """
    head = None
    fields = None

    reader = csv.reader(sys.stdin, delimiter=args.delimiter)
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    for r in reader:
        try:
            if head is None:
                head = r
                fields = r if args.fields is None else args.fields.split()

            tr = [
                e for i, e in enumerate(r)
                if head[i] in fields
            ]

            writer.writerow(map(str, tr))
            sys.stdout.flush()

        except IOError as err:
            if err.errno == errno.EPIPE:
                break


def filter(args):
    """
        cat example.csv | pcsv filter -c 'r.field1 == 1'
    """
    head = None

    reader = csv.reader(sys.stdin, delimiter=args.delimiter)
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    for r in reader:
        try:
            if head is None:
                head = r
                writer.writerow(r)
                sys.stdout.flush()

            else:
                r = map(_convert, r)

                cnd = args.cond
                for i, h in enumerate(head):
                    cnd = re.sub(r'r\.%s([^\w_]*)' % h, r'r[%d]\1' % i, cnd)

                if eval(cnd):
                    writer.writerow(map(str, r))
                    sys.stdout.flush()

        except IOError as err:
            if err.errno == errno.EPIPE:
                break


def extract(args):
    """
        cat example.csv | pcsv extract -e '[r.field1 + r.field2, r.field1 - r.field2]'
    """
    head = None

    reader = csv.reader(sys.stdin, delimiter=args.delimiter)
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    for r in reader:
        try:
            if head is None:
                head = r
                cnt = args.extract.count(',') + 1
                writer.writerow(range(cnt))
                sys.stdout.flush()

            else:
                r = map(_convert, r)

                extr = args.extract
                for i, h in enumerate(head):
                    extr = re.sub(r'r\.%s([^\w_]*)' % h, r'r[%d]\1' % i, extr)

                tr = eval(extr)

                writer.writerow(map(str, tr))
                sys.stdout.flush()

        except IOError as err:
            if err.errno == errno.EPIPE:
                break


def sort(args):
    """
        cat example.csv | pcsv sort -c 'r.field1 + r.field2'
    """
    head = None

    reader = csv.reader(sys.stdin, delimiter=args.delimiter)
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    data = []
    for r in reader:
        try:
            if head is None:
                head = r
                writer.writerow(r)
                sys.stdout.flush()

            else:
                r = map(_convert, r)

                data.append(r)

        except IOError as err:
            if err.errno == errno.EPIPE:
                break

    cnd = args.cond
    for i, h in enumerate(head):
        cnd = re.sub(r'r\.%s([^\w_]*)' % h, r'r[%d]\1' % i, cnd)

    data.sort(key=lambda r: eval(cnd))

    for r in data:
        try:
            writer.writerow(map(str, r))
            sys.stdout.flush()
        except IOError as err:
            if err.errno == errno.EPIPE:
                break


def aggregate(args):
    """
        cat example.csv | pcsv aggregate -k 'r.key1' -b '[0, 0]' -r 'result[0] += 1; result[1] += r.val1;'
    """
    result = {}

    head = None

    reader = csv.reader(sys.stdin, delimiter=args.delimiter)
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    for r in reader:
        try:
            if head is None:
                head = r

            else:
                r = map(_convert, r)

                key = args.key
                for i, h in enumerate(head):
                    key = re.sub(r'r\.%s([^\w_]*)' % h, r'r[%d]\1' % i, key)
                key = eval(key)

                if key not in result:
                    result[key] = eval(args.begin)

                redc = args.reduce
                for i, h in enumerate(head):
                    redc = re.sub(r'r\.%s([^\w_]*)' % h, r'r[%d]\1' % i, redc)
                redc = redc.replace('result[', 'result[key][')

                exec redc

        except IOError as err:
            if err.errno == errno.EPIPE:
                break

    writer.writerow(['key', 'value'])
    sys.stdout.flush()

    for key, value in result.items():
        writer.writerow([key, value])
        sys.stdout.flush()



if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('cmd', help='command name', choices=['count', 'limit', 'select', 'filter', 'extract', 'sort', 'aggregate'])
    parser.add_argument('-d', '--delimiter', help='delimiter', default=',')
    parser.add_argument('-l', '--limit', help='limit', type=int)
    parser.add_argument('-f', '--fields', help='fields')
    parser.add_argument('-c', '--cond', help='condition')
    parser.add_argument('-e', '--extract', help='extract')
    parser.add_argument('-k', '--key', help='key')
    parser.add_argument('-b', '--begin', help='begin')
    parser.add_argument('-r', '--reduce', help='reduce')

    args = parser.parse_args()

    globals()[args.cmd](args)
