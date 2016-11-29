#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sys
import random
import argparse
import logging
import arff
import codecs

logger = None

filename = None
seed = None
fraction = None
attributes = None

attributeIndices = None


def main():

    global logger

    global filename
    global seed
    global fraction
    global attributes

    global attributeIndices

    init()

    logger.info("configuration... filename: %s, fraction: %s, attributes: %s, seed: %s" % (filename, fraction, attributes, seed))

    file = codecs.open(filename, 'rb', 'utf-8')
    arffFile = arff.load(file)

    print("Loaded ARFF file... relation %s has %d attributes and %d data points" % (arffFile['relation'], len(arffFile['attributes']), len(arffFile['data'])))

    attributeIndices = {}

    index = 0
    for attrName, type in arffFile['attributes']:
        attributeIndices[attrName] = index
        index += 1

    if attributes == None:
        attributes = []
        for attrName, type in arffFile['attributes']:
            attributes.append(attrName)

    logger.debug(attributeIndices)

    changedARFF = introduce_missing_values(arffFile)

    outfile = codecs.open(filename + ".missing.arff", 'wb', 'utf-8')
    arff.dump(changedARFF, outfile)

    print("finished")


def introduce_missing_values(arff_file):
    global logger
    print("introduce %d%% missing values in %d attributes..." % (fraction, len(attributes)))

    num = int((len(arff_file['data']) * fraction) / 100)
    logger.debug("fraction=%d -> %d of %d values affected per attribute" % (fraction, num, len(arff_file['data'])))

    allIndices = range(0, len(arff_file['data']))
    logger.debug("allIndices: %s" % allIndices)

    changedARFF = arff_file.copy()

    for attrName in attributes:
        randomIndices = list(allIndices)
        random.shuffle(randomIndices)
        randomIndices = randomIndices[:num]
        logger.debug("random indices: %s" % randomIndices)

        attrIndex = index_of(attrName)

        for dataRowIndex in randomIndices:
            logger.debug("Changed attr %d in row %d to missing" % (attrIndex, dataRowIndex))
            logger.debug("data points: %d" % len(changedARFF['data']))
            logger.debug("data rows: %d" % len(changedARFF['data'][attrIndex]))
            changedARFF['data'][dataRowIndex][attrIndex] = '?'

    return changedARFF




def index_of(attrName):
    if attrName in attributeIndices:
        return attributeIndices[attrName]
    else:
        raise RuntimeError("Attribute name %s unknown" % attrName)



def init():

    global logger
    logging.basicConfig(level=logging.WARN)
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
        if fraction < 1 or fraction > 100:
            raise RuntimeError("Fraction must be a value of 1..100")

    if args.attributes != None:
        attributes = args.attributes

    logger.debug("   params... filename: %s, fraction: %s, attributes: %s, seed: %s" % (args.filename, args.fraction, args.attributes, args.seed))

    if seed != None:
        random.seed(seed)

    if fraction == None:
        fraction = random.randrange(1, 100, 1)

    logger.debug("effective... filename: %s, fraction: %s, attributes: %s, seed: %s" % (filename, fraction, attributes, seed))



main()
