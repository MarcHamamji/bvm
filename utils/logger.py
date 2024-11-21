colors = {
    "black": '\033[30m',
    "red": '\033[31m',
    "green": '\033[32m',
    "orange": '\033[33m',
    "blue": '\033[34m',
    "purple": '\033[35m',
    "cyan": '\033[36m',
    "lightgrey": '\033[37m',
    "darkgrey": '\033[90m',
    "lightred": '\033[91m',
    "lightgreen": '\033[92m',
    "yellow": '\033[93m',
    "lightblue": '\033[94m',
    "pink": '\033[95m',
    "lightcyan": '\033[96m',
    "end": '\033[0m'
}


def colorize(string, color):
    return colors[color] + string + colors['end']


def print_colorized(string, color):
    print(colorize(string, color))


def print_list(title, items):
    if title:
        print(title)
    for item in items:
        print(colorize(" - ", "cyan") + item)


# def print_table(rows):
#     column_names = rows[0].keys()
#
#     column_widths = [max(len(str(row[name])) for row in rows)
#                      for name in column_names]
#     column_widths = [max(len(str(name)), width)
#                      for name, width in zip(column_names, column_widths)]
#
#     separator = "+" + "+".join("-" * (width + 3)
#                                for width in column_widths) + "+"
#
#     print(separator)
#
#     for column_name, width in zip(column_names, column_widths):
#         print("|", end=" ")
#         print(str(column_name).ljust(width), end="  ")
#     print("|")
#
#     print(separator)
#
#     for row in rows:
#         for i, column_name in enumerate(column_names):
#             print("|", end=" ")
#             print(str(row[column_name]).ljust(column_widths[i]), end="  ")
#         print("|")
#
#     print(separator)
