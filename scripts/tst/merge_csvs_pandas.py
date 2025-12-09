#!/usr/bin/env python3
# script to merge two csv files
#
import os, csv
import argparse
import time
import pandas as pd
from merge_csvs_pandas_args import args
                                    
if __name__ == '__main__':

    #just print out the arguments
    print("csvA ->", args.csvA)
    print("csvB ->", args.csvB)
    print("csvM ->", args.csvM)
    csvA = pd.read_csv(args.csvA)
    csvB = pd.read_csv(args.csvB)
    if csvA.shape and csvB.shape:
        print("merging 2 csv files")
        time.sleep(5)
        # Combine them (stack vertically, like appending rows)
        combined = pd.concat([csvA, csvB], ignore_index=True)

        # Save the result to a new CSV file
        combined.to_csv(args.csvM, index=False)
    else:
        print("some csv file couldn't be read")

    
