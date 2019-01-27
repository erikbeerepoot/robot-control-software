from scan.tools.ScanParser import ScanParser
from util.FileUtils import create_directory

import os


class ScanReaderWriter:
    def __init__(self, path):
        self.path = os.path.expanduser(path)
        self.parser = ScanParser()

    def save_scan_data(self, data):
        '''
        Saves scan data to file in binary format
        :param data: The scan data to save
        :return: True if successful False otherwise
        '''
        create_directory(self.path)

        try:
            with open(self.path, 'ab+') as f:
                f.write(data)
        except IOError:
            print(f"Could not open file at path {self.path} for writing.")
            return False

    def load_scan_data(self):
        '''
        Load scan data from file
        :return: the data, or empty array (if data could not be loaded)
        '''
        try:
            with open(self.path, 'rb') as f:
                return f.read()
        except IOError:
            print(f"Could not open file at path {self.path} for reading.")
            return []

    def load_scans(self):
        data = self.load_scan_data().decode("UTF-8")
        return self.parser.parse_scan_data(data)
