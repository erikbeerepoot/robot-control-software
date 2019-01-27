import itertools
import re

from scan.model.Scan import *
from scan.model.ScanError import *


class ScanParser:
    # MS, MD, GS, GD signal the start of a scan
    start_regex = re.compile("(MS|MD|GS|GD)")

    # Double line feed ends a scan
    end_regex = re.compile("\n\n")

    # Regex for all info in the header
    full_header_regex = re.compile("^(MS|MD|GD|GS)([0-9]+)\n([0-9]{2})(.){1}\n(.{5})\n")

    def parse_measurement_params(self, data):
        scan_type = self.start_regex.findall(data)[0]
        if scan_type is None:
            print("Invalid scan type!")
            return None

        # TODO: Validate header length
        sh = ScanParams(
            scan_type,
            int(data[2:6]),
            int(data[6:10]),
            int(data[10:12]),
        )

        if scan_type is "MS" or scan_type is "GS":
            sh.scan_interval = int(data[12:13])
            sh.scan_index = int(data[13:15])

        return sh

    def decode_bytes(self, data):
        d = [ord(byte) - ord('0') for byte in data]

        sum = 0
        for byte in d[:-1]:
            sum |= (0b00111111 & byte)
            sum = sum << 6
        sum |= (0b00111111 & d[-1])
        return sum

    def compute_checksum(self, data):
        '''
        Compute the checksum for a given list of bytes
        :param data: The bytes to compute the checksum for
        :return: The checksum
        '''
        d = [ord(byte) for byte in data]
        return (sum(d) & 0b00111111) + ord('0')

    def parse_status(self, data):
        '''
        Parse the status out of this scan (incomplete implementation)
        :param data:
        :return:
        '''

        if int(data) == 99 or int(data) == 0:
            # 99 is a nominal value for a scan
            # 0 is typically used to confirm the scan command was received
            return ScanStatus("ok")
        else:
            return ScanStatus("error")

    def parse_timestamp(self, data):
        '''
        Parse the timestamp for this scan
        :param data: (trimmed) data containing the timestamp to be parsed
        :return: The decoded timestamp
        '''
        decoded_bytes = self.decode_bytes(data[:-1])
        self.verify_checksum(data)
        return decoded_bytes

    def verify_checksum(self, data):
        '''
        Verify the checksum for a series of bytes
        :param data: The data to verify the checksum for & the checksum itself as the last byte
        :return: Nothing; throws an exception if checksum verification fails.
        '''
        if len(data) < 1:
            return

        checksum = ord(data[-1])
        computed_checksum = self.compute_checksum(data[:-1])
        if checksum is not computed_checksum:
            raise ChecksumError

    def parse_payload(self, data, scan_type):
        '''
        Parse the payload (range data) of this scan
        :param data: The (trimmed) payload data. Should have been extracted from the scan previous
        to passing it to this method.
        :param scan_type: The type of scan we are parsing (retrieved from the header previously)
        :return: The scan payload (list of range values)
        '''
        # The sensor encodes data using either a 2 or 3 character encoding
        # depending on the scan type.
        encoding_char_count = 0
        if scan_type == "MS" or scan_type == "GS":
            encoding_char_count = 2
        elif scan_type == "MD" or scan_type == "GD":
            encoding_char_count = 3

        # Clean up string before processing data
        sanitized_string = data.replace('\x00', '')

        data_segments = sanitized_string.split('\n')
        all_decoded_measurements = []
        for segment in data_segments:
            # Check data integrity before doing any computation
            self.verify_checksum(segment)

            # byte_ranges holds the indices for the bytes to be decoded into measurements
            index_range = list(range(0, len(segment), encoding_char_count))
            byte_ranges = list(zip(index_range[:-1], index_range[1:]))

            # use byte_ranges to get the n-byte tuples to decode
            data_bytes = [segment[range[0]:range[1]] for range in byte_ranges]
            decoded_measurements = [self.decode_bytes(bytes) for bytes in data_bytes]
            all_decoded_measurements.append([measurement for measurement in decoded_measurements])

        non_empty_lists = [x for x in all_decoded_measurements if x]
        return [item for sublist in non_empty_lists for item in sublist]

    def find_scan_boundaries(self, data):
        '''
        Finds all the start & end indices of all the scans in the data passed.
        :param data: The data to parse.
        :return: A list of boundaries [(start, end)] that were found.
        '''
        # 1. Look for start/end substrings
        start_indices = [match.span()[0] for match in ScanParser.start_regex.finditer(data)]
        end_indices = [match.span()[1] for match in ScanParser.end_regex.finditer(data)]

        if len(start_indices) == 0 or len(end_indices) == 0:
            return []

        # 2. Filter start indices where the prefix is not preceded by double line feed and similar for end
        start_indices = list(filter(lambda x: data[x - 1] == '\n' and data[x - 2] == '\n', start_indices))

        last_end_index = end_indices[-1]
        end_indices = list(filter(lambda x: ScanParser.start_regex.findall(data[x:x + 2]), end_indices))
        if last_end_index == len(data):
            end_indices.append(last_end_index)

        if len(start_indices) == 0 or len(end_indices) == 0:
            return []

        # 3. Remove end indices that come before the first starting index (missed start)
        trimmed_end_indices = list(itertools.dropwhile(lambda x: x <= start_indices[0], end_indices))

        # 4. Remove excess starts (missed endings)
        trimmed_start_indices = start_indices[0:len(trimmed_end_indices)]

        # 5. Zip to have a list of (start, end) pairs
        scan_boundaries = list(zip(trimmed_start_indices, trimmed_end_indices))
        return scan_boundaries

    def parse_scan(self, data):
        """
        Parse a single scan
        :param data: The data for this scan
        :return: The scan
        """
        result = self.full_header_regex.findall(data)
        if result is None or len(result) < 1:
            return None
        result = result[0]

        try:
            return Scan(
                self.parse_measurement_params(result[0] + result[1]),
                self.parse_status(result[2]),
                self.parse_timestamp(result[4]),
                self.parse_payload(data[data.index(result[4]) + len(result[4]) + 1:], result[0])
            )
        except ChecksumError:
            return None

    def parse_scan_data(self, data):
        '''
        attempt to parse scan data
        :param data: The scan data we wish to parse
        :return: the parsed scans and the unparsed data that remains
        '''
        if len(data) < 1 or not isinstance(data, str):
            return [], []

        scan_boundaries = self.find_scan_boundaries(data)
        if len(scan_boundaries) == 0:
            return [], []

        # Parse scans from the data
        scans = [self.parse_scan(data[scan_boundary[0]:scan_boundary[1]]) for scan_boundary in scan_boundaries]

        # Return both the scans and the remaining data (so we can attempt to process that later)
        return scans, str(data[scan_boundaries[-1][-1]:])
