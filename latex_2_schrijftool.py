"""Convert latex to plaintext

for use with the KU Leuven Academic Writing Assistant at
https://ilt.kuleuven.be/schrijfhulp/
"""

import pprint
import re

from pylatexenc.latexwalker import LatexWalker,\
    LatexCommentNode, LatexEnvironmentNode, LatexCharsNode, LatexMacroNode

IN_FILE = "tekst.tex"
OUT_FILE = "tekst.txt"

# Pretty printer
pp = pprint.PrettyPrinter(indent=4)

# Regex matches
re_newline = re.compile(r"\s*\n\s*")
re_section = re.compile(r"(?:sub)*section")

# Read latex file
with open(IN_FILE, "r") as fp:
    text = fp.read()

# Parse latex
walker = LatexWalker(text)

# Parse nodes
nodes, pos, length = walker.get_latex_nodes()

# Write output to a file
with open(OUT_FILE, "w") as fp:
    # Number of titles
    num_titles = 0

    # Loop over all nodes
    for node in nodes:
        # Ignore comment nodes
        if isinstance(node, LatexCommentNode):
            # print("Comment:", node.comment)
            continue

        # Ignore certain environments
        if isinstance(node, LatexEnvironmentNode):
            # print(node.environmentname)
            if node.environmentname == "figure":
                continue

        # Parsing normal text
        if isinstance(node, LatexCharsNode):
            paragraph = node.chars.strip()

            # Ignore nodes with only whitespace
            if paragraph == "":
                continue

            # Remove \n and replace by space
            paragraph = re_newline.sub(" ", paragraph)

            fp.write(paragraph)
            fp.write("\n")

        if isinstance(node, LatexMacroNode):
            # If the macro is a (sub)section or etc.
            if re_section.match(node.macroname):
                # Count this title
                num_titles = num_titles + 1

                # Extract section title
                section_title = node.nodeargd.argnlist[2].nodelist[0].chars

                # print("Section title:", section_title)

                fp.write("\n")
                fp.write(section_title)
                fp.write("\n")
                fp.write("\n")

print(f"\nNumber of (sub)titles: { num_titles }")
