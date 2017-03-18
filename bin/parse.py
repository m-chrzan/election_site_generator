from collections import defaultdict
from xlrd import open_workbook

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
            data[district_number][gmina_name][circuit_number] is a dict
            containig the following keys:
                * 'eligible': the number of eligible voters in the circuit
                * 'ballots_given_out', 'ballots_cast', 'ballots_invalid',
                'ballots_valid'
                * 'votes': a dict containing the number of votes for each
                candidate
        """

        data = {}
        for district_number in range(1, 69):
            data[district_number] = self.get_district(district_number)

        return data

    def get_district(self, district_number):
        file_name = 'data/circuits/obw%02d.xls' % district_number
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
        circuits = {}

        for row in range(start_row, sheet.nrows):
            current_gmina_name = sheet.cell_value(row, self.GMINA)
            if current_gmina_name == gmina_name:
                circuit_number = int(sheet.cell_value(row, self.CIRCUIT))
                circuits[circuit_number] = self.get_circuit(sheet, row)
            else:
                break

        return circuits

    def get_circuit(self, sheet, row):
        circuit = {}
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
    return {
        'template': 'mock.html',
        'url': 'mock.html',
        'title': 'Mock',
        'subregions': []
    }
