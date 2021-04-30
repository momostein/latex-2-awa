"""Convert latex to plaintext

for use with the KU Leuven Academic Writing Assistant at
https://ilt.kuleuven.be/schrijfhulp/
"""

import pprint
import re
import argparse

from pylatexenc.latexwalker import LatexWalker,\
    LatexCommentNode, LatexEnvironmentNode, LatexCharsNode, LatexMacroNode, \
    LatexMathNode, LatexSpecialsNode

# Read command line options
parser = argparse.ArgumentParser(
    description="""
        Parse latex to plaintext
        for use with the KU Leuven Academic Writing Assistant at
        https://ilt.kuleuven.be/schrijfhulp/
    """
)

parser.add_argument(
    'input_tex',
    type=str,
    help="Input LaTeX (.tex) file"
)

parser.add_argument(
    'output_txt',
    default="plaintext.txt", type=str,
    help="Output text (.txt) file"
)

parser.add_argument(
    '--no-titles', '-n', dest='no_titles', action='store_true',
    help="Ignore titles (useful for the english tool)"
)

args = parser.parse_args()

input_tex = args.input_tex
output_txt = args.output_txt
no_titles = args.no_titles

# Pretty printer
pp = pprint.PrettyPrinter(indent=4)

# Regex matches
re_newline = re.compile(r"\s*\n\s*")
re_section = re.compile(r"(?:sub)*section|chapter")
re_cite = re.compile(r"cite|(?:page|eq)?ref")
re_new_paragraph = re.compile(r"\n{2,}")

re_double_quote = re.compile(r"``|''")
re_single_quote = re.compile(r"`|'")


def is_symbol(node, LatexMacroNode):
    # TODO: improve this function
    return len(node.macroname) == 1


if __name__ == "__main__":

    # Read latex file
    with open(input_tex, "r") as fp:
        text = fp.read()

    # Parse latex
    walker = LatexWalker(text)

    # Parse nodes
    nodes, pos, length = walker.get_latex_nodes()

    # Write output to a file
    with open(output_txt, "w") as fp:
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
            elif isinstance(node, LatexEnvironmentNode):

                # Dummy environment to just ignore
                if node.environmentname == "no-awa":
                    print("no-awa environment")
                    continue

                # print(node.environmentname)
                if node.environmentname == "figure":
                    continue

            # Parsing normal text
            elif isinstance(node, LatexCharsNode):
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

            elif isinstance(node, LatexMacroNode):
                # If the macro is a (sub)section or etc.
                if re_section.match(node.macroname):
                    if not no_titles:
                        # Count this title
                        num_titles = num_titles + 1

                        # Extract section title
                        section_title = node.nodeargd.argnlist[2].nodelist[0]

                        # print("Section title:", section_title.chars)
                        fp.write("\n\n")
                        fp.write(section_title.chars)
                    continue

                # If the macro is a citation
                elif re_cite.match(node.macroname):
                    print("CITATION")
                    no_new_paragraph = True
                    continue

                elif is_symbol(node):
                    fp.write(" " + node.macroname)
                    no_new_paragraph = True
                    continue

                print("Unknown macro:", node.macroname)

            elif isinstance(node, LatexMathNode):
                # print("Math node:", node)

                if node.displaytype == 'inline':
                    no_new_paragraph = True
                    # fp.write(" INLINE MATH")
                    continue

                print("Unknown display type:", node.displaytype)

            elif isinstance(node, LatexSpecialsNode):
                # Special chars
                if re_double_quote.match(node.specials_chars):
                    fp.write(' "')
                    no_new_paragraph = True
                    continue

                elif re_single_quote.match(node.specials_chars):
                    fp.write(" '")
                    no_new_paragraph = True
                    continue

            else:
                print("Unknown nodetype:", node)

    if not no_titles:
        print(f"\nNumber of (sub)titles: { num_titles }")
