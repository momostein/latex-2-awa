"""Convert latex to plaintext

for use with the KU Leuven Academic Writing Assistant at
https://ilt.kuleuven.be/schrijfhulp/
"""

import pprint
import re

from pylatexenc.latexwalker import LatexWalker,\
    LatexCommentNode, LatexEnvironmentNode, LatexCharsNode, LatexMacroNode

# TODO: Make this a proper command line tool with command line options

IN_FILE = "tekst.tex"
OUT_FILE = "tekst.txt"

# Pretty printer
pp = pprint.PrettyPrinter(indent=4)

# Regex matches
re_newline = re.compile(r"\s*\n\s*")
re_section = re.compile(r"(?:sub)*section")
re_cite = re.compile(r"cite")
re_new_paragraph = re.compile(r"\n{2,}")


def is_symbol(node: LatexMacroNode):
    # TODO: improve this function
    return len(node.macroname) == 1


if __name__ == "__main__":

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

        # If previous node is a citation
        no_new_paragraph = False

        # Loop over all nodes
        for node in nodes:
            # TODO: Implement more rules and process environments recursively

            # Ignore comment nodes
            if isinstance(node, LatexCommentNode):
                # print("Comment:", node.comment)
                continue

            # Ignore certain environments
            if isinstance(node, LatexEnvironmentNode):
                # print(node.environmentname)
                if node.environmentname == "figure":
                    continue

                # Dummy environment to just ignore
                if node.environmentname == "no-awa":
                    print("no-awa environment")
                    continue

            # Parsing normal text
            if isinstance(node, LatexCharsNode):
                new_paragraph = True
                if no_new_paragraph:
                    no_new_paragraph = False
                    # pp.pprint(node.chars)

                    if not re_new_paragraph.match(node.chars):
                        print("No new paragraph")
                        new_paragraph = False

                paragraph = node.chars.strip()

                # Ignore nodes with only whitespace
                if paragraph == "":
                    continue

                # Remove \n and replace by space
                paragraph = re_newline.sub(" ", paragraph)

                # Start a new paragraph if needed, otherwise just add a space
                if new_paragraph:
                    fp.write("\n")
                else:
                    fp.write(" ")

                fp.write(paragraph)

            if isinstance(node, LatexMacroNode):
                # If the macro is a (sub)section or etc.
                if re_section.match(node.macroname):
                    # Count this title
                    num_titles = num_titles + 1

                    # Extract section title
                    section_title = node.nodeargd.argnlist[2].nodelist[0].chars

                    # print("Section title:", section_title)
                    fp.write("\n\n")
                    fp.write(section_title)
                    continue

                # If the macro is a citation
                elif re_cite.match(node.macroname):
                    print("CITATION")
                    no_new_paragraph = True
                    continue

                elif is_symbol(node):
                    fp.write(node.macroname)
                    no_new_paragraph = True
                    continue

                print("Unknown macro:", node.macroname)

    print(f"\nNumber of (sub)titles: { num_titles }")
