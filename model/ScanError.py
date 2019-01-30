class ChecksumError(ValueError):
    '''
    Raise this when the checksum of a series of bytes does not match
    the computed checksum
    '''

