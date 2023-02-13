import argparse
import collections
import os
import pickle
from xml.etree.ElementTree import ElementTree

from lxml import etree


def check_for_duplicate_filenames(filepaths):
    filenames = [file for _, file in filepaths]
    return len(filenames) == len(set(filenames))


def search_file(pattern, path):
    matched_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if pattern in file:
                matched_files.append((root, file))
    matched_files.sort()
    return matched_files


def main(pattern, path, result_dir):
    matched_files = search_file(pattern, path)
    matched_rsps = [(root, file) for root, file in matched_files if
                    "/RSP/" in root]
    file_extensions = set([file.split('.')[-1] for _, file in matched_rsps])
    matched_xmls = [(root, file) for root, file in matched_rsps if
                    file.endswith(".xml")]
    print(f"Numbers of RSP files: {len(matched_rsps)}")
    print(f"File extensions: {file_extensions}")
    print(f"Number of matched XMLs: {len(matched_xmls)}")

    assert check_for_duplicate_filenames(matched_files)

    # doknr: Dokumentennummer
    # doktyp: Dokumententyp
    # gertyp: Gerichtssitz
    # gerort: Gerichtsort
    # aktenzeichen: Aktenzeichen
    # entsch-datum: Entscheidungsdatum
    # ecli: ECLI

    attributes = ["doknr", "doktyp", "gertyp", "gerort", "aktenzeichen",
                  "entsch-datum", "ecli"]

    invalid_files = []
    without_attribute = {attribute: [] for attribute in attributes}

    for root, file in matched_xmls:
        file_path = os.path.join(root, file)

        try:
            xml: ElementTree = etree.parse(file_path)
        except etree.XMLSyntaxError:
            invalid_files.append(file_path)
            continue

        xml_root = xml.getroot()

        for attribute in attributes:
            if attribute == "doknr":
                value = xml_root.get(attribute)
            else:
                value = xml_root.find(f".//{attribute}")
            if value is None:
                without_attribute[attribute].append(file_path)

    # print invalid files
    print(
        f"Invalid files: {len(invalid_files)} ({len(invalid_files) / len(matched_rsps) * 100:.2f}%)")

    # print files without attribute
    for attribute, files in without_attribute.items():
        print(
            f"Without {attribute}: {len(files)} ({len(files) / len(matched_rsps) * 100:.2f}%)")

    os.makedirs(result_dir, exist_ok=True)

    pickle.dump(invalid_files,
                open(os.path.join(result_dir, "invalid_files.pkl"), "wb"))
    pickle.dump(without_attribute,
                open(os.path.join(result_dir, "without_attribute.pkl"), "wb"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--pattern",
                        help="pattern to match e.g. document number",
                        default=".")
    parser.add_argument("-p", "--path", help="path to the dump directory",
                        default="/home/niklas/Documents/dump/")
    parser.add_argument("-d", "--result-dir",
                        help="directory in which results should be written",
                        default="results")
    args = parser.parse_args()

    main(args.pattern, args.path, args.result_dir)

# Example for calling the script
# python parse_dump.py --pattern . -p /home/niklas/Documents/dump/ --result-dir results
