#!/usr/bin/env bash
mongoimport -d=test -c=adtech -u=root -p=root --authenticationDatabase=admin --columnsHaveTypes --type=csv --headerline --file /home/test_mongo.csv --maintainInsertionOrder