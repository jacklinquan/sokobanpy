from pathlib import Path
from xml.etree import ElementTree
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slc_path", help="path to slc file", type=str)
    parser.add_argument("--output", help="path to levels directory", type=str)
    args = parser.parse_args()

    slc_path = Path(args.slc_path)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path.cwd()

    slc_text = slc_path.read_text()
    root = ElementTree.fromstring(slc_text)
    num_levels = len(root.findall("./LevelCollection/Level"))
    num_digits = len(str(abs(num_levels)))
    for i, level in enumerate(root.findall("./LevelCollection/Level")):
        level_string = "\n".join(line.text for line in level.findall("./L"))
        level_file_name = f"{slc_path.stem}_level{str(i+1).zfill(num_digits)}.txt"
        level_file_path = output_path / level_file_name
        level_file_path.write_text(level_string)


if __name__ == "__main__":
    main()
