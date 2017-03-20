#!/bin/bash

mkdir data

# Save into the data directory all .xls files linked on this page
wget -q -P data -r -nd -np -l 1 -A ".xls" \
    http://prezydent2000.pkw.gov.pl/gminy/obwody.html

wget -q -P data prezydent2000.pkw.gov.pl/gminy/zal1.xls
