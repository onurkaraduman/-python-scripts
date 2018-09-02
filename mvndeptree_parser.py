# Parsing `mvn dependency:tree` result and creating nodes
# Dependencies
# pip install anytree==2.4.3
# creating dependency tree file `mvn dependency:tree -DoutputFile <outputFileName>`
# usage `python mvndeptree_parser.py --module <modulePath>`

import argparse
import logging
import os
import subprocess

from anytree import Node, RenderTree, AsciiStyle

logging.basicConfig(format='[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s', level=logging.INFO)

env_var_codebase = "INT_TRUNK"
sign1 = "\-"
sign2 = "+-"
eachLevelDistance = 3

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument("--module", help="module name", required=False)
parser.add_argument("-m", help="module name", required=False)

codebase = os.getenv(env_var_codebase, os.getcwd())


def create_tree(lines_str):
    lines = lines_str.split("\n")
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
            line = line[sign1_index:len(line)]
        elif sign2 in line:
            sign2_index = line.index(sign2) + 3
            level = (sign2_index - previous_sign_index) / eachLevelDistance
            previous_sign_index = sign2_index
            line = line[sign2_index:len(line)]

        reference_node = add_to_tree(reference_node, line, level)

    logging.debug("----DependencyTree-----\n" + RenderTree(parent_node, style=AsciiStyle()).by_attr())
    return parent_node


def add_to_tree(reference_node, line, level):
    if not line:
        return
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

    dependency_props = line.split(":")
    kwargs = {'group_id': dependency_props[0], 'artifact_id': dependency_props[1], 'version': dependency_props[3]}
    return Node(kwargs, parent=temp_reference)


def execute_command(command):
    logging.info("Executing: '" + command + "'")
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    logging.debug(result.stdout)
    return result


def get_dependency_tree(module):
    """
    run 'mvn dependency:tree' and get all dependency list as string
    :param module:
    :return:
    """
    logging.info("Getting dependency tree as string")
    pom = os.path.join(module, "pom.xml")
    cmd = execute_command('mvn dependency:tree -f' + pom)
    start_fill = False
    dependency_list = list()
    for line in cmd.stdout:
        if "maven-dependency-plugin" in line:
            start_fill = True
            continue
        if start_fill == True and "-------------" in line:
            break
        if start_fill:
            dependency_list.append(line.replace("[INFO] ", ""))

    dependency_content = "".join(dependency_list)
    logging.debug("------Full dependency list-------\n" + dependency_content)
    return dependency_content


def main():
    args = parser.parse_args()
    if args.module is None:
        module = os.getcwd()
    else:
        module = args.module
    dependencies = get_dependency_tree(module)
    create_tree(dependencies)


if __name__ == "__main__":
    main()

