# pcsv

A simple utility working with CSV-files in terminal.
The advantage is that very big CSV-files can be processed without consuming a lot of RAM,
because the utility gets data line by line through `stdin`.

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

    cat example.csv | pcsv count
    5
    
### 2. limit -l LIMIT

    $ cat example.csv | pcsv limit -l 3
    id,name,team,score1,score2
    1,Alex,A,5.5,1.2
    2,Steve,B,4.1,5.0
    3,John,A,6.8,2.2
    
### 3. select -f 'FIELD1 FIELD2'

    $ cat example.csv | pcsv select -f 'name score1'
    name,score1
    Alex,5.5
    Steve,4.1
    John,6.8
    Bill,5.1
    Jack,6.1
    
### 4. filter -c 'COND'

    $ cat example.csv | pcsv filter -c 'r.score1 + r.score2 > 9.0'
    id,name,team,score1,score2
    2,Steve,B,4.1,5.0
    5,Jack,B,6.1,4.8
    
### 5. extract -e '[EXPR1, EXPR2, ...]'

    $ cat example.csv | pcsv extract -e '[r.name, r.score1 + r.score2]'
    0,1
    Alex,6.7
    Steve,9.1
    John,9.0
    Bill,8.6
    Jack,10.9
    
### 6. sort -c 'KEY_EXPR'

    $ cat example.csv | pcsv sort -c 'r.score1 + r.score2'
    id,name,score1,score2
    1,Alex,A,5.5,1.2
    4,Bill,A,5.1,3.5
    3,John,A,6.8,2.2
    2,Steve,B,4.1,5.0
    5,Jack,B,6.1,4.8
    
### 7. aggregate -k 'KEY_EXPR' -b 'START_EXPR' -r 'ADD_EXPR'

    $ cat example.csv | pcsv aggregate -k 0 -b '{"score1_sum": 0, "score2_sum": 0, "score_sum": 0}' -r 'result["score1_sum"] += r.score1; result["score2_sum"] += r.score2; result["score_sum"] += r.score1 + r.score2'
    key,value
    0,"{'score2_sum': 16.7, 'score1_sum': 27.6, 'score_sum': 44.3}"
    
    $ cat example.csv | pcsv aggregate -k 'r.team' -b '{"score1_sum": 0, "score2_sum": 0, "score_sum": 0}' -r 'result["score1_sum"] += r.score1; result["score2_sum"] += r.score2; result["score_sum"] += r.score1 + r.score2'
    key,value
    A,"{'score2_sum': 6.9, 'score1_sum': 17.4, 'score_sum': 24.3}"
    B,"{'score2_sum': 9.8, 'score1_sum': 10.2, 'score_sum': 20.0}"
