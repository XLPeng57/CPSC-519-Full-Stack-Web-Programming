"""
This program will take a crn of a course as an input, and print details
about it, including the course title, description, prerequisites, other
sections, crosslistings, and the instructors.
"""

import argparse
import sys
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
            sys.exit(0)

        return info

    except Error as error:
        print(error, file=sys.stderr)
        sys.exit(1)


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
        print(error, file=sys.stderr)
        sys.exit(1)


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
        print(error, file=sys.stderr)
        sys.exit(1)


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
        print(error, file=sys.stderr)
        sys.exit(1)


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
        print(error, file=sys.stderr)
        sys.exit(1)


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
        print(error, file=sys.stderr)
        sys.exit(1)


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
        print(error, file=sys.stderr)
        sys.exit(1)


def output(col, data):
    """
    generate a table with given colomn headers and data
    """
    my_table = table.Table(col, data)
    print(my_table)
    print()


def main():
    """ main function """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'crn', type=int, help='the id of the course whose details should be shown', nargs=1)

    args = parser.parse_args()
    course_crn = args.crn[0]

    course_info = get_course_info(course_crn)
    course_title = get_course_title(course_crn)
    course_descrip = get_course_desc(course_crn)
    course_prereqs = get_course_prereqs(course_crn)
    course_sections = get_course_sections(course_crn)
    course_crosslist = get_course_crosslist(course_crn)
    course_profs = get_course_prof(course_crn)

    output(["deptcode", "deptname", "subjectcode", "coursenum"], course_info)
    output(["title"], course_title)
    output(["descrip"], course_descrip)
    output(["prereqs"], course_prereqs)
    output(["sectionnumber", "crn", "meetinginfo"], course_sections)
    output(["subjectcode", "coursenum"], course_crosslist)
    output(["professors"], course_profs)


if __name__ == "__main__":

    main()
