"""
Produce a table of information the user asked
"""
import sys
from sqlite3 import connect, Error
from contextlib import closing
import argparse
import table


def generate_statement():
    '''get command-line input and return a statement'''

    parser = argparse.ArgumentParser(allow_abbrev = False)
    parser.add_argument('-d',
                        metavar = 'deptcode',
                        type = str,
                        help = 'show only those classes whose department code contains dept')
    parser.add_argument('-s',
                        metavar = 'subjectcode',
                        type = str,
                        help = 'show only those classes whose subjectcode contains subject')
    parser.add_argument('-n',
                        metavar = 'num',
                        type = int,
                        help = 'show only those classes whose course number contains num')
    parser.add_argument('-t',
                        metavar = 'title',
                        type = str,
                        help = 'show only those classes whose course title contains title')

    args, _ = parser.parse_known_args()

    stmt_str = "SELECT deptname, subjectcode, coursenum, title, crn "
    stmt_str += "FROM courses "
    stmt_str += "NATURAL JOIN sections "
    stmt_str += "NATURAL JOIN departments "

    i = 0
    attributes = ['deptcode', 'subjectcode', 'coursenum', 'title']
    first = True
    for arg in vars(args):
        arg_value = getattr(args, arg)
        if arg_value is not None and first:
            stmt_str +=  "WHERE " + attributes[i] + " LIKE '%" + str(arg_value) + "%' "
            first = False
        elif arg_value is not None and not first:
            stmt_str +=  "AND " + attributes[i] + " LIKE '%" + str(arg_value) + "%' "
        i += 1

    if "WHERE" not in stmt_str:
        print("Please provide legal arguments")
        sys.exit(1)

    stmt_str += "COLLATE NOCASE "
    stmt_str += "ORDER BY deptname, subjectcode, coursenum, title, crn ASC "
    return stmt_str

def generate_data(stmt_str):
    '''get statement string and get data from database'''

    # some lines are copied and modified from authorsearch.py in demo files

    try:
        with connect("reg.sqlite", isolation_level=None, uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(stmt_str)
                rows = cursor.fetchall()

    except Error as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    columns = ['deptname', 'subject', 'num', 'title', 'crns']

    if rows is None:
        print("Failed to fetch data.")
        sys.exit(1)

    elif len(rows) == 0:
        print("No results.")
        sys.exit(0)

    else:
        data = [list(r) for r in rows]

        for i, row in enumerate(data):
            row[2] = str(row[2])
            row[4] = str(row[4])

        for i in range(len(data)-1, -1, -1):
            if i > 0 and data[i][0:4] == data[i-1][0:4]:
                data[i-1][4] += '|' + data[i][4]
                data.pop(i)

    return (columns, data)


def output_table(columns, data):
    '''get columns and data and output a table'''
    my_table = table.Table(columns, data, format_str='wwwwp')
    print(my_table)


def main():
    '''main function'''
    stmt_str = generate_statement()
    columns, data = generate_data(stmt_str)
    output_table(columns, data)


if __name__ == "__main__":
    main()
