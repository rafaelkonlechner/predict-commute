#!/usr/bin/python3.5
# -*- coding: iso-8859-15 -*-

import sys
import random
import argparse
import logging
import arff	# liac-arff, see: https://github.com/renatopp/liac-arff
import codecs

logger = None

filename = None
seed = None
fraction = None
attributesAffected = None
replaceMissingValuesWithClassMean = False

allAttributes = None
classAttribute = None
attributeIndices = None


def main():

    global logger

    global filename
    global seed
    global fraction
    global attributesAffected
    global replaceMissingValuesWithClassMean

    global attributeIndices
    global classAttribute
    global allAttributes

    init()

    logger.info("configuration... filename: %s, fraction: %s, attributes: %s, seed: %s" % (filename, fraction, attributesAffected, seed))

    file = codecs.open(filename, 'rb', 'utf-8')
    arffFile = arff.load(file)

    print("Loaded ARFF file... relation %s has %d attributes and %d data points" % (arffFile['relation'], len(arffFile['attributes']), len(arffFile['data'])))

    attributeIndices = {}

    index = 0
    for attrName, type in arffFile['attributes']:
        attributeIndices[attrName] = index
        index += 1

    if attributesAffected == None:
        attributesAffected = []
        for attrName, type in arffFile['attributes']:
            attributesAffected.append(attrName)

    allAttributes = []
    for attrName, type in arffFile['attributes']:
        allAttributes.append((attrName, type))
    classAttribute = allAttributes[-1]

    allAttributes.remove(classAttribute)

    if classAttribute[0] in attributesAffected:
        attributesAffected.remove(classAttribute[0])

    if fraction == 0:
        changedARFF = arffFile
    else:
        changedARFF = introduce_missing_values(arffFile)

    if replaceMissingValuesWithClassMean:
        changedARFF = doReplaceMissingValuesWithClassMean(changedARFF)
        fileExtension = ".missing.replaced.arff"
    else:
        fileExtension = ".missing.arff"


    outfile = codecs.open(filename + fileExtension, 'wb', 'utf-8')
    arff.dump(changedARFF, outfile)

    print("finished")


def doReplaceMissingValuesWithClassMean(arff_file):
    global logger
    global allAttributes
    global classAttribute

    print("replace missing values with class mean...")

    result = arff_file.copy()

    logger.info("class attribute is %s" % classAttribute[0])

    classValues = classAttribute[1]

    logger.info("class values: %s" % classValues)

    attrValueCount = {}
    attrValueSum = {}
    for attrName, type in allAttributes:
        attrValueCount[attrName] = {}
        attrValueSum[attrName] = {}
        for classValue in classValues:
            attrValueCount[attrName][classValue] = 0
            if type == "NUMERIC":
                attrValueSum[attrName][classValue] = 0.0
            else:
                attrValueSum[attrName][classValue] = {}
                for pval in type:
                    attrValueSum[attrName][classValue][pval] = 0


    for row in arff_file['data']:
        rowClass = row[-1]
        for attrName, type in allAttributes:
            attr_index = index_of(attrName)
            if row[attr_index] != None:
                attrValueCount[attrName][rowClass] += 1
                if type == "NUMERIC":
                    attrValueSum[attrName][rowClass] += float(row[attr_index])
                else:
                    attrValueSum[attrName][rowClass][row[attr_index]] += 1

    classMeans = {}
    for attrName, type in allAttributes:
        attr_index = index_of(attrName)
        classMeans[attrName] = {}
        for classValue in classValues:
            if type == "NUMERIC":
                if attrValueCount[attrName][classValue] == 0:
                    classMeans[attrName][classValue] = None
                else:
                    classMeans[attrName][classValue] = attrValueSum[attrName][classValue] / attrValueCount[attrName][classValue]
            else:
                max = (None, -1)
                for attrValue, count in attrValueSum[attrName][classValue].items():
                    if classValue != None and count > max[1]:
                        max = (attrValue, count)

                classMeans[attrName][classValue] = max[0]

    for attrName, type in allAttributes:
        logger.debug("\n\nmeans of %s: %s" % (attrName, classMeans[attrName]))

    for row in result['data']:
        rowClass = row[-1]
        for attrName, type in allAttributes:
            attr_index = index_of(attrName)
            if row[attr_index] == None:
                row[attr_index] = classMeans[attrName][rowClass]

    return result



def introduce_missing_values(arff_file):
    global logger
    print("introduce %d%% missing values in %d attributes %s..." % (fraction, len(attributesAffected), attributesAffected))

    num = int((len(arff_file['data']) * fraction) / 100)
    logger.debug("fraction=%d -> %d of %d values affected per attribute" % (fraction, num, len(arff_file['data'])))

    allIndices = range(0, len(arff_file['data']))
    logger.debug("allIndices: %s" % allIndices)

    changedARFF = arff_file.copy()

    for attrName in attributesAffected:
        randomIndices = list(allIndices)
        random.shuffle(randomIndices)
        randomIndices = randomIndices[:num]
        logger.debug("random indices: %s" % randomIndices)

        attrIndex = index_of(attrName)

        for dataRowIndex in randomIndices:
            logger.debug("Changed attr %d in row %d to missing" % (attrIndex, dataRowIndex))
            changedARFF['data'][dataRowIndex][attrIndex] = None

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
    global attributesAffected
    global replaceMissingValuesWithClassMean

    parser = argparse.ArgumentParser(description='Update an ARFF file to change some values to missing ("?")')
    parser.add_argument('filename', type=str, nargs=1)
    parser.add_argument('--fraction', '-f', metavar='fr', type=int, nargs=1,
                        help='percentage of missing values to introduce (0..100)')
    parser.add_argument('--attributes', '-a', metavar='attrName', type=str, nargs='+', help='names of target attributes')
    parser.add_argument('--seed', '-s', metavar='seed', type=int, nargs=1,
                        help='seed of the random generator (>1) (default: random)')
    parser.add_argument('--replaceMissingValuesMeanClass', '-r', type=bool, nargs=1,
                        help='will replace missing values with the mean attribute value of the class (default: false)')

    args = parser.parse_args()

    filename = args.filename[0]

    if args.seed != None:
        seed = args.seed[0]

    if args.fraction != None:
        fraction = args.fraction[0]
        if fraction < 0 or fraction > 100:
            raise RuntimeError("Fraction must be a value of 0..100")

    if args.attributes != None:
        attributesAffected = args.attributes

    replaceMissingValuesWithClassMean = args.replaceMissingValuesMeanClass != None \
                                        and args.replaceMissingValuesMeanClass[0] == True

    logger.debug("   params... filename: %s, fraction: %s, attributes: %s, seed: %s, replaceMissingValues: %s" % (args.filename, args.fraction, args.attributes, args.seed, args.replaceMissingValuesMeanClass))

    if seed != None:
        random.seed(seed)

    if fraction == None:
        fraction = random.randrange(1, 100, 1)

    logger.debug("effective... filename: %s, fraction: %s, attributes: %s, seed: %s, replaceMissingValues: %s" % (filename, fraction, attributesAffected, seed, replaceMissingValuesWithClassMean))



main()
