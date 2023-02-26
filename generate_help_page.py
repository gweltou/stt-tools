#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from libMySTT import list_files_with_extension



if __name__ == "__main__":
    split_files = list_files_with_extension(".split", ".")
    print(split_files)
