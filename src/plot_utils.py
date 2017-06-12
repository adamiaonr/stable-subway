import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import argparse
import sys
import glob

import xml.etree.cElementTree as et

from datetime import date
from datetime import datetime
from collections import defaultdict
from collections import OrderedDict
from itertools import chain, izip

# interface event codes
EVENT_NLM = 0 # no link matches
EVENT_MLM = 1 # multiple link matches
EVENT_LLM = 2 # local link match
EVENT_SLM = 3 # single link match (other than local)
EVENT_TTL = 4 # drop due to rtt expiration

# outcome codes
OUTCOME_CORRECT_DELIVERY     = 0
OUTCOME_INCORRECT_DELIVERY   = 1
OUTCOME_FALLBACK_DELIVERY    = 2
OUTCOME_FALLBACK_RELAY       = 3
OUTCOME_PACKET_DROP          = 4
OUTCOME_TTL_DROP             = 5
OUTCOME_UNDEF                = 6

ileave = lambda *iters: list(chain(*izip(*iters)))

# full method with doctests
def interleave_n(*iters):
    """
    Given two or more iterables, return a list containing 
    the elements of the input list interleaved.
    
    >>> x = [1, 2, 3, 4]
    >>> y = ('a', 'b', 'c', 'd')
    >>> interleave(x, x)
    [1, 1, 2, 2, 3, 3, 4, 4]
    >>> interleave(x, y, x)
    [1, 'a', 1, 2, 'b', 2, 3, 'c', 3, 4, 'd', 4]
    
    On a list of lists:
    >>> interleave(*[x, x])
    [1, 1, 2, 2, 3, 3, 4, 4]
    
    Note that inputs of different lengths will cause the 
    result to be truncated at the length of the shortest iterable.
    >>> z = [9, 8, 7]
    >>> interleave(x, z)
    [1, 9, 2, 8, 3, 7]
    
    On single iterable, or nothing:
    >>> interleave(x)
    [1, 2, 3, 4]
    >>> interleave()
    []
    """
    return list(chain(*izip(*iters)))

def interleave(a, b):
    c = list(zip(a, b))
    return [elt for sublist in c for elt in sublist]

def move_to_processed(data_dir):

    for file_name in sorted(glob.glob(os.path.join(os.path.join(data_dir, "unprocessed"), '*.tsv'))):
        os.rename(file_name, os.path.join(os.path.join(data_dir, "processed"), file_name.split("/")[-1]))

def extract_data(data_dir):

    """ given a dir w/ .tsv files, extracts data from .tsv file into 
    a hash table of data frames, indexed by session id """

    data = defaultdict(OrderedDict)

    data_dir = os.path.join(data_dir, "unprocessed")
    for file_name in sorted(glob.glob(os.path.join(data_dir, '*.tsv'))):

        session_id = file_name.split(".")[0].split("_", 2)[-1]
        print("filename = %s, session_id = %s" % (file_name, session_id))
        data[session_id] = pd.read_csv(file_name, sep = "\t")
        data[session_id] = data[session_id].convert_objects(convert_numeric = True)
        # convert timestamp column to datetime obj
        # data[session_id]['accelerometer.seconds.Unix'] = pd.to_datetime(data[session_id]['accelerometer.seconds.Unix'], unit = 's')
        # rename columns
        data[session_id].columns = ['n', 'session', 'time', 'acc-xx', 'acc-yy', 'acc-zz', 'acc-total', 'event-type', 'event-descr']

    return data
