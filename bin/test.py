from selenium import webdriver
from os import getcwd
from random import shuffle
from collections import defaultdict

def check_page(level = 0):
    current_url = browser.current_url
    check_links_ok()
    browser.get(current_url)
    if level < 3:
        check_votes_sum()
        browser.get(current_url)

    urls = get_subpage_urls()
    for url in select_up_to_3_random(urls):
        browser.get(url)
        check_page(level + 1)
        browser.get(current_url)

def select_up_to_3_random(urls):
    if len(urls) <= 3:
        return urls
    else:
        shuffle(urls)
        return urls[:3]

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
    browser.get(url)

    assert (name + " | Wybory Prezydenta Rzeczypospolitej Polskiej 2000" ==
        browser.title)

    browser.back()

def get_subpage_urls():
    """Returns a list of urls to each subpage of the current page"""
    return [link.get_attribute('href') for link in
        browser.find_elements_by_tag_name('#turnout a')
    ]

def check_votes_sum():
    """Checks that the sum of the votes on the subpages equals the number of
    votes on the current page"""
    votes = get_votes()

    expected_votes = sum_subpage_votes()

    for candidate in votes:
        assert votes[candidate] == expected_votes[candidate]

def get_votes():
    votes = {}

    candidates = [data.get_attribute('innerHTML') for data in
        browser.find_elements_by_css_selector( '#results td:first-child')]
    vote_amounts = [int(data.get_attribute('innerHTML')) for data in
        browser.find_elements_by_css_selector('#results td:nth-child(2)')]

    for candidate, vote_amount in zip(candidates, vote_amounts):
        votes[candidate] = vote_amount

    return votes

def sum_subpage_votes():
    votes = defaultdict(lambda: 0)
    urls = get_subpage_urls()

    for url in urls:
        browser.get(url)

        sub_votes = get_votes()
        for candidate in sub_votes:
            votes[candidate] += sub_votes[candidate]

        browser.back()

    return votes

browser = webdriver.Firefox()
browser.get('file://' + getcwd() + '/html/Polska.html')
check_page()
