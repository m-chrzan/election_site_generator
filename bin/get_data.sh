#!/bin/bash

mkdir data
mkdir data/gminas
mkdir data/circuits


# Save into the data/gminas directory all .xls files linked on this page
wget -q -P data/gminas -r -nd -np -l 1 -A ".xls" \
    http://prezydent2000.pkw.gov.pl/gminy/gminy.html

# Save into the data/circuits directory all .xls files linked on this page
wget -q -P data/circuits -r -nd -np -l 1 -A ".xls" \
    http://prezydent2000.pkw.gov.pl/gminy/obwody.html
