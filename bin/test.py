from selenium import webdriver
import os
import time
from collections import defaultdict

def do_and_wait(action):
    action()
    time.sleep(0.1)

def check_page(name):
    assert (name + " | Wybory Prezydenta Rzeczypospolitej Polskiej 2000" ==
        browser.title)

    check_links_ok()

def check_links_ok():
    """Checks that each link on the page leads to an existing site, and that
    each of these sites has a correctly formatted title that matches the link's
    text"""

    urls_with_names = [
        (link.get_attribute('href'), link.get_attribute('innerHTML').strip())
        for link in browser.find_elements_by_tag_name("a")
    ]

    for (url, name) in urls_with_names:
        check_subpage_has_correct_title(url, name)

def check_subpage_has_correct_title(url, name):
    do_and_wait(lambda: browser.get(url))

    assert (name + " | Wybory Prezydenta Rzeczypospolitej Polskiej 2000" ==
        browser.title)

    do_and_wait(lambda: browser.back())

browser = webdriver.Firefox()
browser.get('file://' + os.getcwd() + '/html/Polska.html')
check_page("Polska")
