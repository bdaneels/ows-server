#!/usr/bin/env python3
# script to merge two csv files
#
import os, csv
import argparse
import time

def read_csv(fname):
    rows = []
    if os.path.exists(fname):
        with open(fname, newline='\n') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                rows.append(row)
    else:
        print(f"csv file {fname} does not exist")
    return rows
                                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #first two arguments are required
    parser.add_argument("csvA", help="first CSV file")
    parser.add_argument("csvB", help="second csv file")
    parser.add_argument("csvM", help="merged csv output filename")

    args = parser.parse_args()
    #just print out the arguments
    print("csvA ->", args.csvA)
    print("csvB ->", args.csvB)
    print("csvM ->", args.csvM)
    csvA = read_csv(args.csvA)
    csvB = read_csv(args.csvB)
    if csvA and csvB:
        print("merging 2 csv files")
        time.sleep(5)
        with open(args.csvM, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in csvA:
                writer.writerow(row)
            for row in csvB:
                writer.writerow(row)
        #now read the merged csv and print some stuff
        csvM = read_csv(args.csvM)
        for row in csvM:
            print(row)
    else:
        print("some csv file couldn't be read")

    
