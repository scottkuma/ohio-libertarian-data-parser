#!/bin/bash

sqlite3 -header -csv $1 "select * from Libertarians;" > $2
