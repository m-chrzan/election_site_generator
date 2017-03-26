from collections import defaultdict
from xlrd import open_workbook

data = {}

class RegionGetter:
    """Abstract class defining defaults for regional getters.

    Each of RegionGetter's subclasses is responsible for collecting and
    structuring the voting data for a specific region. This class defines a
    sensible defualt constructor, several constants used throughout the data
    structuring process, and helper methods.
    """
    VOIVODESHIP_NAME_COLUMN = 1
    INDICATOR_COLUMN = 0
    VOIVODESHIPS_START_ROW = 6

    def __init__(self):
        self.context = {
            'subregions': [],
            'with_map': False,
            'superregion': None
        }

    def set_voting_data(self, source = 'subregions'):
        """Derive several data points from the data collected in subregions."""
        data_points = ['eligible', 'ballots_given_out', 'ballots_cast',
            'ballots_invalid', 'ballots_valid']

        for data_point in data_points:
            self.context[data_point] = 0

        for subregion in self.context[source]:
            for data_point in data_points:
                self.context[data_point] += subregion[data_point]

        self.context['turnout'] = (self.context['ballots_given_out'] /
            self.context['eligible'])

    def set_votes(self, source = 'subregions'):
        """Set the number of votes for each candidate based on data from
        subregions."""
        self.context['votes'] = defaultdict(lambda: 0)

        for subregion in self.context[source]:
            for candidate in subregion['votes']:
                self.context['votes'][candidate] += subregion['votes'][candidate]

        self.context['percentage_votes'] = {}
        for candidate in self.context['votes']:
            self.context['percentage_votes'][candidate] = \
                self.context['votes'][candidate] / self.context['ballots_valid']

class CountryGetter(RegionGetter):
    def __init__(self):
        super().__init__()
        self.context['with_map'] = True
        self.context['locative'] = 'kraju'
        self.context['name'] = 'Polska'
        self.context['subregions'] = self.get_voivodeships()
        self.context['level'] = 0

        self.set_voting_data()
        self.set_votes()

    def get_voivodeships(self):
        voivodeships = []

        sheet = open_workbook('data/zal1.xls').sheet_by_index(0)

        for row in range(self.VOIVODESHIPS_START_ROW, sheet.nrows):
            indicator = sheet.cell_value(row, self.INDICATOR_COLUMN)
            if indicator == 'województwo':
                voivodeship_name = sheet.cell_value(row,
                        self.VOIVODESHIP_NAME_COLUMN)
                disctrict_numbers = self.get_district_numbers(sheet, row + 1)
                voivodeship = VoivodeshipGetter(self.context,
                        voivodeship_name, disctrict_numbers).context
                voivodeships.append(voivodeship)

        return voivodeships

    def get_district_numbers(self, sheet, row):
        district_numbers = []

        while True:
            indicator = sheet.cell_value(row, self.INDICATOR_COLUMN)
            row += 1
            if indicator == 'województwo':
                break
            else:
                district_numbers.append(str(int(indicator)))

            if row >= sheet.nrows:
                break

        return district_numbers

class VoivodeshipGetter(RegionGetter):
    def __init__(self, superregion, name, district_numbers):
        super().__init__()
        self.context['locative'] = 'województwie'
        self.context['superregion'] = superregion
        self.context['name'] = name
        self.context['level'] = 1
        for district_number in district_numbers:
            district = DistrictGetter(self.context, district_number).context
            self.context['subregions'].append(district)

        self.set_voting_data()
        self.set_votes()

class DistrictGetter(RegionGetter):
    def __init__(self, superregion, number):
        super().__init__()
        self.context['locative'] = 'okręgu'
        self.context['superregion'] = superregion
        self.context['name'] = "Okręg nr. " + number
        self.context['number'] = number
        self.context['level'] = 2
        gmina_names = self.get_gmina_names()
        for gmina_name in gmina_names:
            gmina = GminaGetter(self.context, gmina_name).context
            self.context['subregions'].append(gmina)

        self.set_voting_data()
        self.set_votes()

    def get_gmina_names(self):
        return data[self.context['number']].keys()

class GminaGetter(RegionGetter):
    def __init__(self, superregion, name):
        super().__init__()
        self.context['locative'] = 'gminie'
        self.context['superregion'] = superregion
        self.context['name'] = name
        self.context['level'] = 3
        self.context['circuits'] = data[superregion['number']][name]
        self.set_voting_data('circuits')
        self.set_votes('circuits')

class XlsParser:
    CANDIDATE_NAMES_ROW = 0
    # Column numbers for various data points
    DISTRICT = 0
    GMINA = 2
    CIRCUIT = 4
    ELIGIBLE = 7
    BALLOTS_GIVEN_OUT = 8
    BALLOTS_CAST = 9
    BALLOTS_INVALID = 10
    BALLOTS_VALID = 11
    CANDIDATES_START = 12

    def get_data(self):
        """Reads the circuit files and returns a dict containing the data.

        Strucutre of the dict:
            data[district_number][gmina_name] is a list of dicts containing data
            about individual circuits with the following keys:
                * 'name': the circuit's number
                * 'eligible': the number of eligible voters in the circuit
                * 'ballots_given_out', 'ballots_cast', 'ballots_invalid',
                'ballots_valid'
                * 'votes': a dict containing the number of votes for each
                candidate
        """

        data = {}
        for district_number in range(1, 69):
            data[str(district_number)] = self.get_district(district_number)

        return data

    def get_district(self, district_number):
        file_name = 'data/obw%02d.xls' % district_number
        sheet = open_workbook(file_name).sheet_by_index(0)

        return self.get_gminas(sheet)

    def get_gminas(self, sheet):
        gminas = defaultdict(lambda: None)

        for row in range(1, sheet.nrows):
            gmina_name = sheet.cell_value(row, self.GMINA)
            if not gminas[gmina_name]:
                gminas[gmina_name] = self.get_circuits(sheet, gmina_name, row)

        return gminas

    def get_circuits(self, sheet, gmina_name, start_row):
        circuits = []

        for row in range(start_row, sheet.nrows):
            current_gmina_name = sheet.cell_value(row, self.GMINA)
            if current_gmina_name == gmina_name:
                circuits.append(self.get_circuit(sheet, row))
            else:
                break

        return circuits

    def get_circuit(self, sheet, row):
        circuit = {}

        circuit['name'] = int(sheet.cell_value(row, self.CIRCUIT))
        circuit['eligible'] = int(sheet.cell_value(row, self.ELIGIBLE))
        circuit['ballots_given_out'] = int(sheet.cell_value(row,
            self.BALLOTS_GIVEN_OUT))
        circuit['ballots_cast'] = int(sheet.cell_value(row, self.BALLOTS_CAST))
        circuit['ballots_invalid'] = int(sheet.cell_value(row,
            self.BALLOTS_INVALID))
        circuit['ballots_valid'] = int(sheet.cell_value(row,
            self.BALLOTS_VALID))

        circuit['votes'] = self.get_votes(sheet, row)

        return circuit

    def get_votes(self, sheet, row):
        votes = {}

        for column in range(self.CANDIDATES_START, sheet.ncols):
            candidate_name = sheet.cell_value(self.CANDIDATE_NAMES_ROW, column)
            votes[candidate_name] = int(sheet.cell_value(row, column))

        return votes

def parse():
    """Returns a Region dict containing data about the elections."""
    global data
    data = XlsParser().get_data()
    cg = CountryGetter()
    return cg.context
