import os


def create_directory(path):
    directory = os.path.dirname(os.path.expanduser(path))
    if not os.path.exists(directory):
        os.makedirs(directory)
