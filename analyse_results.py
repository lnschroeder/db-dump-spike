import argparse
import os
import pickle
from pprint import pprint


def main(result_dir, verbose=False):
    with open(os.path.join(result_dir, "invalid_files.pkl"), "rb") as f:
        invalid_files = pickle.load(f)

    print(f"Invalid files: {len(invalid_files)}")
    if verbose:
        pprint(invalid_files[:5])

    with open(os.path.join(result_dir, "without_attribute.pkl"), "rb") as f:
        without_attribute = pickle.load(f)

    for attribute, files in without_attribute.items():
        print(f"Without {attribute}: {len(files)}")
        if verbose:
            pprint(files[:5] if len(files) < 5 else files[:5] + ["..."])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--result-dir", help="directory with the results",
                        default="results")
    parser.add_argument("-v", "--verbose", help="print more information",
                        action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    main(args.result_dir, verbose=args.verbose)

# Example for calling the script
# python analyse_results.py -d results -v
