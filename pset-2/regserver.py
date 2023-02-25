from sys import stderr, exit
import os
import socket
import argparse
from sqlite3 import connect, Error
from contextlib import closing
import table

DATABASE_URL = "reg.sqlite"


def get_course_info(crn):
    """
    get the course info, including deptcode, deptname, subjectcode, and coursenum
    """

    info = []

    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT courses.deptcode, deptname, subjectcode, coursenum "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "NATURAL JOIN departments "
                stmt_str += "WHERE sections.crn = ? "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    info.append(row)
                    row = cursor.fetchone()

        if len(info) == 0:
            print("No Course Found.")
            return ""

        return info

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_title(crn):
    """
    get the course title
    """
    title = []
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT title "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE sections.crn = ? "
                # stmt_str += "AND courses.courseid = sections.courseid "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    title.append(row)
                    row = cursor.fetchone()
        return title

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_desc(crn):
    """
    get the course description
    """
    descrip = []

    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT descrip "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE sections.crn = ? "
                # stmt_str += "AND courses.courseid = sections.courseid "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    descrip.append(row)
                    row = cursor.fetchone()
        return descrip

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_prereqs(crn):
    """
    get the course prerequisites
    """
    prereqs = []
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT prereqs "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE sections.crn = ? "
                # stmt_str += "AND courses.courseid = sections.courseid "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    prereqs.append(row)
                    row = cursor.fetchone()
        return prereqs

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_sections(crn):
    """
    get the course seciton number, crn, time, and location
    """
    sections = []
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT sectionnumber, crn, timestring || ' @ ' || locstring AS meeting "
                stmt_str += "FROM sections "
                stmt_str += "NATURAL JOIN courses "
                stmt_str += "NATURAL JOIN meetings "
                stmt_str += "WHERE courseid = "
                stmt_str += "(SELECT courseid FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE crn = ?) "
                stmt_str += "ORDER BY sectionnumber, crn ASC "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()

                if row is not None:
                    cur_num = row[0]
                    cur_crn = row[1]

                while row is not None:
                    if len(sections) > 0 and cur_num == row[0] and cur_crn == row[1]:
                        sections.append(["", "", row[2]])
                    else:
                        sections.append(row)
                        cur_num = row[0]
                        cur_crn = row[1]

                    row = cursor.fetchone()
        return sections

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_crosslist(crn):
    """
    get the course crosslistings
    """

    subject = []

    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT subjectcode, coursenum "
                stmt_str += "FROM courses NATURAL JOIN crosslistings "
                stmt_str += "WHERE crosslistings.secondarycourseid = courses.courseid "
                stmt_str += "AND crosslistings.primarycourseid =  "
                stmt_str += "(SELECT courseid FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE crn = ?)"
                stmt_str += "ORDER BY subjectcode, coursenum ASC "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    subject.append(row)
                    row = cursor.fetchone()

        return subject

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_prof(crn):
    """
    get the course instructors
    """

    profs = []
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT profname "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "NATURAL JOIN coursesprofs "
                stmt_str += "NATURAL JOIN profs "
                stmt_str += "WHERE sections.crn = ? "
                stmt_str += "ORDER BY profname "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    profs.append(row)
                    row = cursor.fetchone()
        return profs

    except Error as error:
        print(error, file=stderr)
        exit(1)


def output(col, data):
    """
    generate a table with given colomn headers and data
    """
    my_table = table.Table(col, data)
    return str(my_table)


def generate_detail_table(course_crn):
    """ generate course detail table """

    course_info = get_course_info(course_crn)
    course_title = get_course_title(course_crn)
    course_descrip = get_course_desc(course_crn)
    course_prereqs = get_course_prereqs(course_crn)
    course_sections = get_course_sections(course_crn)
    course_crosslist = get_course_crosslist(course_crn)
    course_profs = get_course_prof(course_crn)

    result = str(output(["deptcode", "deptname", "subjectcode",
                         "coursenum"], course_info)) + "\n\n"
    result += str(output(["title"], course_title)) + "\n\n"
    result += str(output(["descrip"], course_descrip)) + "\n\n"
    result += str(output(["prereqs"], course_prereqs)) + "\n\n"
    result += str(output(["sectionnumber", "crn",
                  "meetinginfo"], course_sections)) + "\n\n"
    result += str(output(["subjectcode", "coursenum"],
                  course_crosslist)) + "\n\n"
    result += str(output(["professors"], course_profs)) + "\n\n"

    return result


def generate_string(line):
    """
    generate a string to send to the client
    """

    if line.find("crn:") != -1:
        i = line.find("crn:") + 4
        course_crn = ""
        while (line[i]) != "\n":
            course_crn += line[i]
            i += 1
        result = generate_detail_table(course_crn)

    else:
        result = generate_course_table(line)

    return result


def generate_course_table(line):
    """
    get statement string and get data from database
    """

    # some lines are copied and modified from authorsearch.py in demo files

    stmt_str = generate_statement(line)

    try:
        with connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(stmt_str)
                rows = cursor.fetchall()

    except Error as error:
        print(error, file=stderr)
        exit(1)

    columns = ['crn', 'deptname', 'subject', 'num', 'title']

    if rows is None:
        print("Failed to fetch data.")
        exit(1)

    elif len(rows) == 0:
        print("No results.")
        return ""

    else:
        data = [list(r) for r in rows]

        for _, row in enumerate(data):
            row[2] = str(row[2])
            row[4] = str(row[4])

    course_table = table.Table(columns, data, max_width=500)

    return str(course_table)


def generate_statement(line):
    """
    get command-line input and return a statement
    """

    arguments = []

    if line.find("dept:") != -1:
        i = line.find("dept:") + 5
        term = "deptcode LIKE '%"
        while (line[i+1]) != "#" or (line[i+2]) != "#":
            term += line[i]
            i += 1
        term += line[i]
        term += "%' "
        arguments.append(term)

    if line.find("coursenum:") != -1:
        i = line.find("coursenum:") + 10
        term = "coursenum LIKE '%"
        while (line[i+1]) != "#" or (line[i+2]) != "#":
            term += line[i]
            i += 1
        term += line[i]
        term += "%' "
        arguments.append(term)

    if line.find("subject:") != -1:
        i = line.find("subject:") + 8
        term = "subjectcode LIKE '%"
        while (line[i+1]) != "#" or (line[i+2]) != "#":
            term += line[i]
            i += 1
        term += line[i]
        term += "%' "
        arguments.append(term)

    if line.find("title:") != -1:
        i = line.find("title:") + 6
        term = "title LIKE '%"
        while (line[i+1]) != "#" or (line[i+2]) != "#":
            term += line[i]
            i += 1
        term += line[i]
        term += "%' "
        arguments.append(term)

    stmt_str = "SELECT crn, deptname, subjectcode, coursenum, title "
    stmt_str += "FROM courses "
    stmt_str += "NATURAL JOIN sections "
    stmt_str += "NATURAL JOIN departments "

    first = True
    if line != " \n" and len(arguments) > 0:
        for arg in arguments:
            if first:
                stmt_str += "WHERE " + arg
                first = False
            else:
                stmt_str += "AND " + arg
        stmt_str += "COLLATE NOCASE "

    stmt_str += "ORDER BY deptname, subjectcode, coursenum, title, crn ASC "

    return stmt_str


def handle_client(sock):
    """
    handles client request
    """
    in_flo = sock.makefile(mode='r')
    lines = in_flo.readline()

    result = generate_string(lines)
    out_flo = sock.makefile(mode='w', encoding='utf-8')
    out_flo.write(result)
    out_flo.flush()


def main():
    """
    main function to initiate server and listen to client
    """
    try:
        parser = argparse.ArgumentParser(
            allow_abbrev=False, description='Server for the registrar application')
        parser.add_argument('port',
                            type=int,
                            nargs=1,
                            help='the port at which the server should listen')
        args = parser.parse_args()
        port = args.port[0]
        server_socket = socket.socket()

        if os.name != 'nt':
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind(('', port))
        except Exception as ex:
            print(ex, file=stderr)
            exit(1)
        server_socket.listen()

        while True:
            try:
                sock, _ = server_socket.accept()
                with sock:
                    handle_client(sock)
            except Exception as ex:
                print(ex, file=stderr)
                exit(1)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
