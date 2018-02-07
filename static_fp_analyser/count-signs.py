#!/usr/bin/env python3
import sys
import glob
import os
from script import Script

sorting = True
path_file_js_functions = os.path.abspath('js-functions.txt')

if len(sys.argv) != 2:
    print("Need exactly 1 argument: a dir containing the domain dirs")
    sys.exit(1)
if not os.path.isdir(sys.argv[1]):
    print("{0} is not a directory.".format(sys.argv[1]))
    sys.exit(2)

start_dir = os.path.abspath(sys.argv[1])
if not start_dir.endswith("/"):
    start_dir += "/"

print("Base dir: {0}".format(start_dir))


def get_dict_fp_functions():
    temp = open(path_file_js_functions, 'r').read().split('\n')
    functions = {}
    for f in temp:
        if not f.startswith('#') and f:
            f_split = f.split(",")
            functions[f_split[0]] = [int(f_split[1]), 0]
    return functions


def count_domain(path_domain):
    os.chdir(path_domain)
    current_dir_name = os.path.basename(os.getcwd())
    print("[Entered domain {0}]".format(current_dir_name))
    scripts = []

    # Collect files within domain
    for dob_file in glob.iglob(path_domain + '**/*.dob', recursive=True):
        scripts.append(Script(dob_file, get_dict_fp_functions()))

    for exp_file in glob.iglob(path_domain + '**/*.exp', recursive=True):
        scripts.append(Script(exp_file, get_dict_fp_functions()))

    # Count total
    total_count = get_dict_fp_functions()
    for script in scripts:
        for k, v in script.fp_functions.items():
            if script.file_path.endswith('.dob'):
                # .dob: only count not expanded values (flag=1)
                if v[0] == 1:
                    total_count[k][1] += v[1]
            elif script.file_path.endswith('exp'):
                # .exp: only count expanded values (flag=0)
                if v[0] == 0:
                    total_count[k][1] += v[1]

    # Save total to file
    out_file_name = "total-count.txt"
    if sorting:
        with open(out_file_name, "w") as f:
            s = [(k, total_count[k]) for k in
                 sorted(total_count, key=total_count.get, reverse=True)]
            for k, v in s:
                f.write(k + "," + str(v[1]) + "\n")
    else:
        with open(out_file_name, "w") as f:
            for k, v in total_count.items():
                f.write(k + "," + str(v[1]) + "\n")
    print("Saved count results for {0}".format(current_dir_name))


domains = glob.glob(start_dir + "*/")
for domain in domains:
    count_domain(domain)
