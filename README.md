# pcsv

A minimalistic utility to work with heavy CSV-files in terminal. It takes data from `stdin` and outputs the result into `stdout`. It does not consume a lot of RAM because it does not need to keep whole CVS file in memory. Below there are some example of how it can be used.


## Tutorial

Supposing we have a following CSV-file:

    $ cat example.csv
    id,name,team,score1,score2
    1,Alex,A,5.5,1.2
    2,Steve,B,4.1,5.0
    3,John,A,6.8,2.2
    4,Bill,A,5.1,3.5
    5,Jack,B,6.1,4.8

### 1. count

    $ cat example.csv | pcsv --head count
    5

### 2. limit -l LIMIT

    $ cat example.csv | pcsv --head limit -l 3
    id,name,team,score1,score2
    1,Alex,A,5.5,1.2
    2,Steve,B,4.1,5.0
    3,John,A,6.8,2.2

### 3. select -f 'FIELD1 FIELD2'

    $ cat example.csv | pcsv --head select -f 'name score1'
    name,score1
    Alex,5.5
    Steve,4.1
    John,6.8
    Bill,5.1
    Jack,6.1

### 4. filter -c 'COND'

    $ cat example.csv | pcsv --head filter -c 'r["score1"] + r["score2"] > 9.0'
    id,name,team,score1,score2
    2,Steve,B,4.1,5.0
    5,Jack,B,6.1,4.8

### 5. extract -e '[EXPR1, EXPR2, ...]'

    $ cat example.csv | pcsv --head extract -e '[r["name"], r["score1"] + r["score2"]]'
    0,1
    Alex,6.7
    Steve,9.1
    John,9.0
    Bill,8.6
    Jack,10.9

### 6. sort -c 'KEY_EXPR'

    $ cat example.csv | pcsv --head sort -k 'r["score1"] + r["score2"]'
    id,name,score1,score2
    1,Alex,A,5.5,1.2
    4,Bill,A,5.1,3.5
    3,John,A,6.8,2.2
    2,Steve,B,4.1,5.0
    5,Jack,B,6.1,4.8

### 7. aggregate -k 'KEY_EXPR' -b 'START_EXPR' -r 'ADD_EXPR'

    $ cat example.csv | pcsv --head aggregate -r '__result__ += r["score1"]'
    0,27.6

    $ cat example.csv | pcsv --head aggregate -b '{"score1_sum": 0, "score2_sum": 0}' -r '__result__["score1_sum"] += r["score1"]; __result__["score2_sum"] += r["score2"]'
    0,"{'score1_sum': 27.6, 'score2_sum': 16.7}"

    $ cat example.csv | pcsv --head aggregate -k 'r["team"]' -r '__result__ += r["score1"] + r["score2"]'
    A,24.3
    B,20.0
