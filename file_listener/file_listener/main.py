from listener.folder_listener import observe_folder

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='File changes listener')
    parser.add_argument('folder_to_listen')

    args = parser.parse_args()

    observe_folder(args.folder_to_listen)
