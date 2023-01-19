#!/usr/bin/env python3

"""qslots
Author(s): Jason C. McDonald

Track time beautifully.
"""

import logging

import matplotlib

from qslots.interface import interface

logging.basicConfig(level=logging.INFO)


def main():
    return interface.run()


if __name__ == "__main__":
    main()
