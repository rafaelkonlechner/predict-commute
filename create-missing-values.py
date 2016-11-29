#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sys
import random
import argparse
import logging

logger = None

filename = None
seed = None
fraction = None
attributes = None

def main():

    global logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    global filename
    global seed
    global fraction
    global attributes

    parser = argparse.ArgumentParser(description='Update an ARFF file to change some values to missing ("?")')
    parser.add_argument('filename', type=str, nargs=1)
    parser.add_argument('--fraction', '-f', metavar='fr', type=int, nargs=1,
                        help='percentage of missing values to introduce (1..100)')
    parser.add_argument('--attributes', '-a', metavar='attrName', type=str, nargs='+', help='names of target attributes')
    parser.add_argument('--seed', '-s', metavar='seed', type=int, nargs=1,
                        help='seed of the random generator (>1) (default: random)')

    args = parser.parse_args()

    filename = args.filename[0]

    if args.seed != None:
        seed = args.seed[0]

    if args.fraction != None:
        fraction = args.fraction[0]

    if args.attributes != None:
        attributes = args.attributes

    logger.debug("   params... filename: %s, fraction: %s, attributes: %s, seed: %s" % (args.filename, args.fraction, args.attributes, args.seed))

    if seed != None:
        random.seed(seed)

    if fraction == None:
        fraction = random.randrange(1, 100, 1)

    logger.debug("effective... filename: %s, fraction: %s, attributes: %s, seed: %s" % (filename, fraction, attributes, seed))

# /main


main()
