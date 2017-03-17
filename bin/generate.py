import os
import subprocess
from jinja2 import Environment, FileSystemLoader, select_autoescape

from parse import parse

def get_data():
    """Executes a bash script that downloads the necessary data into data/."""
    if not os.path.isdir("data"):
        subprocess.run("bin/get_data.sh")

def parse_data():
    """Parses the .xls files in data/.

    Returns: Region object representing the entire country."""
    return parse()

def generate_region(region, jinja_env):
    """Generates a region's html page.

    The page will be saved to a file specified by the region object.
    Args:
        region (Region): the object containing data about the region whose page
            is to be generated.
        jinja_env: the Jinja environment providing templates for generation.
    """
    template = jinja_env.get_template(region['template'])
    rendered = template.render(region)

    output_file = open('html/' + region['url'], 'w')
    output_file.write(rendered)

def generate_all_regions(top_region, jinja_env):
    """Generates all regions' sites.

    Recursively descends into the top_region object, generating sites for the
    top region and all its subregions.

    Args:
        top_region (Region): the region whose, and whose subregions, sites are
            to be generated.
        jinja_env: the Jinja environment providing templates for generation.
    """

    generate_region(top_region, jinja_env)

    for region in top_region['subregions']:
        generate_region(region, jinja_env)

if __name__ == '__main__':
    get_data()

    country = parse_data()

    jinja_env = Environment(
        loader = FileSystemLoader('templates'),
        autoescape = select_autoescape(['html'])
    )

    generate_all_regions(country, jinja_env)
