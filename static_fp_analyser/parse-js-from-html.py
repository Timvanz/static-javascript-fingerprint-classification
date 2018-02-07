#!/usr/bin/env Python3
from bs4 import BeautifulSoup
import glob
import os
import sys

if len(sys.argv) != 2:
    print("Need exactly 1 argument: a directory from where the script looks "
          "for HTML files.")
    sys.exit(1)
if not os.path.isdir(sys.argv[1]):
    print("{0} is not a directory.".format(sys.argv[1]))
    sys.exit(2)

start_dir = sys.argv[1]
if not start_dir.endswith("/"):
    start_dir += "/"

print("Looking for HTML files under directory \"{0}\"".format(start_dir))

for html_file in glob.iglob(start_dir + '**/*.html', recursive=True):
    print("Processing {0}...".format(html_file))
    html = open(html_file, 'rb').read()
    soup = BeautifulSoup(html, "lxml")
    js_code = soup.findAll('script')

    js_code_as_list = []
    for script in js_code:
        js_code_as_list.append(str(script.getText()))
    out_file_name = os.path.splitext(html_file)[0] + ".js"
    with open(out_file_name, 'w') as out_file:
        out_file.write("\n".join(js_code_as_list))
