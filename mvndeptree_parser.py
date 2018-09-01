# Parsing `mvn dependency:tree` result and creating nodes
# Dependencies
# pip install anytree==2.4.3
# creating dependency tree file `mvn dependency:tree -DoutputFile <outputFileName>`
# usage `python mvndeptree_parser.py --dfile <DependencyTreeFile>`

import sys
import argparse
from anytree import Node, RenderTree, AsciiStyle

sign1 = "\-"
sign2 = "+-"
eachLevelDistance = 3

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument("--dfile", help="dependency file", required=True)


def create_tree(lines):
    previous_sign_index = 0
    parent_node = Node(lines[0])
    reference_node = parent_node
    for i in range(1, len(lines)):
        line = lines[i]
        level = 0
        if sign1 in line:
            sign1_index = line.index(sign1) + 3
            level = (sign1_index - previous_sign_index) / eachLevelDistance
            previous_sign_index = sign1_index
            line = line.replace(sign1, "")
        elif sign2 in line:
            sign2_index = line.index(sign2) + 3
            level = (sign2_index - previous_sign_index) / eachLevelDistance
            previous_sign_index = sign2_index
            line = line.replace(sign2, "")

        reference_node = add_to_tree(reference_node, line, level)

    print(RenderTree(parent_node, style=AsciiStyle()).by_attr())
    return parent_node


def add_to_tree(reference_node, line, level):
    temp_reference = reference_node
    if level < 0:
        for level_counter in range(0, abs(level) + 1):
            temp_reference = temp_reference.parent
            level_counter += 1
    elif level > 0:
        for level_counter in range(1, level):
            temp_reference = temp_reference.descendants[0]
            level_counter += 1
    else:
        temp_reference = temp_reference.parent

    return Node(line, parent=temp_reference)


def main(arg):
    args = parser.parse_args()
    filePath = args.dfile
    file = open(filePath, "r")
    lines = file.readlines()
    create_tree(lines)


if __name__ == "__main__":
    main(sys.argv)

