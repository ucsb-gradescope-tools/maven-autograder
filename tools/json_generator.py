#!/usr/bin/env python3

import json
import argparse
import os
from pathlib import Path


########################################################################################
# This python script is a helper to generate informational results.json output in the 
# proper Gradescope format. The ideal use is that several results.json files are 
# generated throughout the autograder's run and then they are combined at the very end. 
# These are created with a score of 0/1 or 0/0 only.
#
# NOTE: This script does not write to files. We pipe to a file in shell instead.
########################################################################################

# Initialize command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--title", help="Result title")
parser.add_argument("-b", "--body", help="Result body")
parser.add_argument("-i", "--input", help="Input file to read as results body instead of --body")
parser.add_argument("-c", "--combine", help="Combine all the json files in a specified folder and produce a single combined output")
parser.add_argument("-p", "--passtest", help="Grade the test as 0/0 (passing). If not set, the grade will be 0/1", action='store_true')

args = parser.parse_args()

if args.input == None and args.title != None:
    bod = ""
    max_score = 1
    if args.body != None:
        bod = args.body
    if args.passtest == True:
        max_score = 0
    the_test = {"name": args.title, "max_score": max_score, "score": 0  , "output": bod}
    json_output_as_dict = { "tests" : [ the_test ] }
    print(json.dumps(json_output_as_dict,indent=2,sort_keys=True))
    exit(0)

if args.input != None:
    with open(args.input,'r') as infile:
        f = infile.read()
        # Gradescope truncates files > 100,000 chars and maven outputs are longer
        # The bottom half of the file tends to be more useful, so let's just keep that
        if len(f) > 99990:
            f = f[-99990:]
        the_test = {"name": args.title, "max_score": 1, "score": 0  , "output": f}
        json_output_as_dict = { "tests" : [ the_test ] }
        print(json.dumps(json_output_as_dict,indent=2,sort_keys=True))
        exit(0)

# Prints out the combination of all json files in the given directory
if args.combine != None:
    results = []
    # json files sorted by creation date
    json_files = [p for p in sorted(os.listdir(args.combine), key=lambda x: os.path.getctime(os.path.join(args.combine, x))) if p.endswith(".json")]
    for json_file in json_files:
        with open(os.path.join(args.combine, json_file)) as f:
            try:
                data = json.load(f)
                results.extend(data["tests"])
            except:
                print("[json_generator] Unable to read", json_file, ", skipping")
    json_output_as_dict = { "tests" : results }
    with open(os.path.join(args.combine, "results.json"), 'w') as outfile:
        json.dump(json_output_as_dict, outfile,indent=2,sort_keys=True)
    print("Found: ", json_files)
    exit(0)
