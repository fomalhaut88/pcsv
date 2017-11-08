import re
import csv
from copy import deepcopy
from argparse import ArgumentParser


class Pcsv:
    COMMANDS = ['count', 'limit', 'select', 'filter', 'extract', 'sort', 'aggregate']

    def __init__(self, args):
        self._args = args

        self._head = []
        self._result = []
        self._state = {}
        self._leave = False

    def pipe(self, sin, sout):
        del self._head[:]
        del self._result[:]
        self._state.clear()
        self._leave = False

        proc = self._row_processor()
        proc.send(None)

        reader = csv.reader(sin)
        writer = csv.writer(sout)
        for row in reader:
            rownew = proc.send(row)

            if rownew is not None:
                writer.writerow(rownew)

            if self._leave:
                break

        for resrow in self._result:
            writer.writerow(resrow)

    def _row_processor(self):
        result = None
        while True:
            row = yield result
            result = self._handle(row)

    def _handle(self, row):
        routine = self._get_routine(self._args.cmd)
        return routine(row)

    def _get_routine(self, name):
        return getattr(self, '_' + name)

    def _create_head(self, row):
        if self._args.head:
            return row
        else:
            return list(range(len(row)))

    def _get_index(self, field):
        if field.isdigit():
            return int(field)
        else:
            return self._head.index(field)

    def _replace_fields(self, expr):
        if self._head:
            for i, f in enumerate(self._head):
                expr = re.sub(r'r\[[\'\"]%s[\'\"]\]' % f, r'r[%d]' % i, expr)
        return expr

    @classmethod
    def _convert(cls, e):
        try:
            return eval(e)
        except Exception:
            return e

    @classmethod
    def _sorting_insert(cls, lst, e, key):
        index = 0
        size = len(lst)
        ke = key(e)

        while size > 0:
            m = index + size // 2
            km = key(lst[m])
            if km < ke:
                index = m + 1
                size = size - size // 2 - 1
            else:
                size = size // 2

        lst.insert(index, e)

    def _count(self, row):
        """
        cat example.csv | pcsv --head count
        """
        if not self._result:
            init_value = -1 if self._args.head else 0
            self._result.append([init_value])
        self._result[0][0] += 1

    def _limit(self, row):
        """
        cat example.csv | pcsv --head limit -l 3
        """
        if 'counter' not in self._state:
            init_value = -1 if self._args.head else 0
            self._state['counter'] = init_value
        self._state['counter'] += 1
        if self._state['counter'] >= self._args.limit:
            self._leave = True
        return row

    def _select(self, row):
        """
        cat example.csv | pcsv --head select -f 'name 0 score1'
        """
        if not self._head:
            self._head = self._create_head(row)

        if 'indices' not in self._state:
            fields = self._args.fields.split()
            self._state['indices'] = [self._get_index(f) for f in fields]

        return [row[i] for i in self._state['indices']]

    def _filter(self, row):
        """
        cat example.csv | pcsv --head filter -c 'r["score1"] + r["score2"] > 9.0'
        """
        if not self._head:
            self._head = self._create_head(row)
            if self._args.head:
                return row

        if 'cond' not in self._state:
            self._state['cond'] = self._replace_fields(self._args.cond)

        r = list(map(self._convert, row))
        if eval(self._state['cond']):
            return row

    def _extract(self, row):
        """
        cat example.csv | pcsv --head extract -e '[r["name"], r["score1"] + r["score2"]]'
        """
        if not self._head:
            self._head = self._create_head(row)
            if self._args.head:
                return

        if 'extract' not in self._state:
            self._state['extract'] = self._replace_fields(self._args.extract)

        r = list(map(self._convert, row))
        return eval(self._state['extract'])

    def _sort(self, row):
        """
        cat example.csv | pcsv --head sort -k 'r["score1"] + r["score2"]'
        """
        if not self._head:
            self._head = self._create_head(row)
            if self._args.head:
                return row

        if 'key' not in self._state:
            self._state['key'] = self._replace_fields(self._args.key)

        r = list(map(self._convert, row))
        self._sorting_insert(self._result, r, key=lambda r: eval(self._state['key']))

    def _aggregate(self, row):
        """
        cat example.csv | pcsv --head aggregate -r '__result__ += r["score1"]'
        cat example.csv | pcsv --head aggregate -b '{"score1_sum": 0, "score2_sum": 0}' -r '__result__["score1_sum"] += r["score1"]; __result__["score2_sum"] += r["score2"]'
        cat example.csv | pcsv --head aggregate -k 'r["team"]' -r '__result__ += r["score1"] + r["score2"]'
        """
        if not self._head:
            self._head = self._create_head(row)
            if self._args.head:
                return

        if 'key' not in self._state:
            self._state['key'] = self._replace_fields(self._args.key)

        if 'begin' not in self._state:
            self._state['begin'] = eval(self._replace_fields(self._args.begin))

        if 'reduce' not in self._state:
            self._state['reduce'] = self._replace_fields(self._args.reduce)

        if 'result_map' not in self._state:
            self._state['result_map'] = {}

        r = list(map(self._convert, row))

        key = eval(self._state['key'])

        if key not in self._state['result_map']:
            self._state['result_map'][key] = len(self._result)
            entry = deepcopy(self._state['begin'])
            self._result.append([key, entry])

        index = self._state['result_map'][key]

        ns = {
            '__result__': self._result[index][1],
            'r': r
        }
        exec(self._state['reduce'], ns)
        self._result[index][1] = ns['__result__']
