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

def generate_path(region):
    if region['superregion'] == None:
        return [region]
    else:
        return generate_path(region['superregion']) + [region]

def generate_url(region):
    path = generate_path(region)
    new_path = []
    for region in path:
        segment = region['name']
        new_path.append(prepare_for_url(segment))

    return '/'.join(new_path) + '.html'

def generate_rel_url(region1, region2):
    """Generates a relative URL from region1 to region2.

    If region1.level >= region2.level, assumes that region1 is a subregion of
    region2.
    If region1.level < region2.level, assumes that region2 is a direct subregion
    of region1.
    """
    name1 = prepare_for_url(region1['name'])
    name2 = prepare_for_url(region2['name'])
    level_difference = region1['level'] - region2['level']
    if level_difference >= 0:
        go_up = '../' * level_difference
        return go_up + name2 + '.html'
    else:
        return name1 + '/' + name2 + '.html'

def prepare_for_url(string):
    string = remove_polish_letters(string)
    string = remove_spaces(string)
    string = remove_periods(string)
    return string

def transliterate(string, frm, to, delete = ''):
    trans_table = str.maketrans(frm, to, delete)
    return string.translate(trans_table)

def remove_polish_letters(string):
    return transliterate(string, 'ęóąśłżźćńĘÓĄŚŁŻŹĆŃ', 'eoaslzzcnEOASLZZCN')

def remove_spaces(string):
    return transliterate(string, ' ', '_')

def remove_periods(string):
    return transliterate(string, '', '', '.')

def generate_region(region, jinja_env):
    """Generates a region's html page.

    The page will be saved to a file specified by the region object.
    Args:
        region (Region): the object containing data about the region whose page
            is to be generated.
        jinja_env: the Jinja environment providing templates for generation.
    """
    if region['with_map']:
        template = jinja_env.get_template('with_map.html')
    else:
        template = jinja_env.get_template('without_map.html')

    helpers = {
        'generate_path': generate_path,
        'generate_rel_url': generate_rel_url,
    }

    rendered = template.render(region = region, helpers = helpers)

    filename = 'html/' + generate_url(region)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    output_file = open(filename, 'w')
    output_file.write(rendered)
    output_file.close()

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
        generate_all_regions(region, jinja_env)

if __name__ == '__main__':
    get_data()

    country = parse_data()

    jinja_env = Environment(
        loader = FileSystemLoader('templates'),
        autoescape = select_autoescape(['html'])
    )

    generate_all_regions(country, jinja_env)
