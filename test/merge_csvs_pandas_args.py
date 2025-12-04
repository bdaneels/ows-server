import argparse

parser = argparse.ArgumentParser()
#first two arguments are required
parser.add_argument("csvA", help="first CSV file")
parser.add_argument("csvB", help="second csv file")
parser.add_argument("csvM", help="merged csv output filename")
args = parser.parse_args()
