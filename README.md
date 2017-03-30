# 2000 Polish Presidential Elections site generator

Using data from the [official election site](http://prezydent2000.pkw.gov.pl/wyniki.html),
`bin/generate.py` will generate a static HTML site presenting the data, with
subpages for each voivodeship, electoral disctrict, and gmina. 

## Running

    git clone https://github.com/m-chrzan/elections_generator
    cd elections_generator
    python bin/generate.py

The resulting HTML will be placed in an `html/` directory, and the downloaded
data will be in `data/`.

## Testing

    python bin/test.py

The testing script requires [Selenium bindings for Python](https://pypi.python.org/pypi/selenium)
and [geckodriver](https://github.com/mozilla/geckodriver).

## Dependencies

* [Python](https://www.python.org/) 3.5
* [Jinja](http://jinja.pocoo.org/) 2.9.5
* [xlrd](http://xlrd.readthedocs.io/en/latest/) 1.0.0
