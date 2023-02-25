from sys import stderr, exit
from sqlite3 import connect, Error
from contextlib import closing
from course import Course, CourseDetail

DATABASE_URL = "reg.sqlite"


def get_course_info(crn, res):
    """
    get the course info, including deptcode, deptname, subjectcode, and coursenum
    """

    info = []

    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "SELECT deptname, subjectcode, coursenum "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "NATURAL JOIN departments "
                stmt_str += "WHERE sections.crn = ? "
                cursor.execute(stmt_str, [crn])

                row = cursor.fetchone()
                while row is not None:
                    # info.append(row)
                    res.set_deptname(str(row[0]))
                    res.set_subjectcode(str(row[1]))
                    res.set_coursenum(str(row[2]))
                    row = cursor.fetchone()

        if len(info) == 0:
            print("No Course Found.")
            return ""

        return info

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_title(crn, res):
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
                    # title.append(row)
                    res.set_title(str(row[0]))
                    row = cursor.fetchone()
        return title

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_desc(crn, res):
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
                    # descrip.append(row)
                    res.set_descrip(str(row[0]))
                    row = cursor.fetchone()
        return descrip

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_prereqs(crn, res):
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
                    res.set_prereqs(str(row[0]))
                    row = cursor.fetchone()
        return prereqs

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_sections(crn, res):
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

                while row is not None:
                    res.set_sections(tuple(row))
                    row = cursor.fetchone()

                    row = cursor.fetchone()
        return sections

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_crosslist(crn, res):
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
                    res.set_crosslist(tuple(row))
                    row = cursor.fetchone()

        return subject

    except Error as error:
        print(error, file=stderr)
        exit(1)


def get_course_prof(crn, res):
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
                    res.set_profs(str(row[0]))
                    row = cursor.fetchone()
        return profs

    except Error as error:
        print(error, file=stderr)
        exit(1)


def generate_course_table(dept, coursenum, subject, title):
    """
    get statement string and get course data from database
    """

    #---------------------------------------------------------------#
    # some lines are copied and modified from regserver.py in pset2 #
    # some structures are borrowed from flask demo files            #
    #---------------------------------------------------------------#

    courses = []

    stmt_str = generate_statement(dept, coursenum, subject, title)

    try:
        with connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(stmt_str)
                row = cursor.fetchone()

                if row is None:
                    print("No results.")
                    return courses

                while row is not None:
                    course = Course(str(row[0]), str(row[1]), str(
                        row[2]), str(row[3]), str(row[4]))
                    courses.append(course)
                    row = cursor.fetchone()

    except Error as error:
        print(error, file=stderr)
        exit(1)

    return courses


def generate_statement(dept, coursenum, subject, title):
    """
    get command-line input and return a statement for course search
    """

    arguments = []

    if dept is not None:
        term = "deptname LIKE '%"
        term += dept
        term += "%' "
        arguments.append(term)

    if coursenum is not None:
        term = "coursenum LIKE '%"
        term += coursenum
        term += "%' "
        arguments.append(term)

    if subject is not None:
        term = "subjectcode LIKE '%"
        term += subject
        term += "%' "
        arguments.append(term)

    if title is not None:
        term = "title LIKE '%"
        term += title
        term += "%' "
        arguments.append(term)

    stmt_str = "SELECT crn, deptname, subjectcode, coursenum, title "
    stmt_str += "FROM courses "
    stmt_str += "NATURAL JOIN sections "
    stmt_str += "NATURAL JOIN departments "

    first = True
    if len(arguments) > 0:
        for arg in arguments:
            if first:
                stmt_str += "WHERE " + arg
                first = False
            else:
                stmt_str += "AND " + arg
        stmt_str += "COLLATE NOCASE "

    stmt_str += "ORDER BY deptname, coursenum, crn ASC "

    return stmt_str


def search(dept, coursenum, subject, title):
    """
    generate a string to send to the client
    """

    # if input.find("crn:") != -1:
    #     i = input.find("crn:") + 4
    #     course_crn = ""
    #     while (input[i]) != "\n":
    #         course_crn += input[i]
    #         i += 1
    #     result = generate_detail_table(course_crn)

    # else:

    result = generate_course_table(dept, coursenum, subject, title)

    return result


def search_detail(crn):
    """
    generate a string to send to the client
    """

    # else:
    result = CourseDetail(crn)
    get_course_info(crn, result)
    get_course_title(crn, result)
    get_course_desc(crn, result)
    get_course_prereqs(crn, result)
    get_course_sections(crn, result)
    get_course_crosslist(crn, result)
    get_course_prof(crn, result)

    return result


def update_title(user_input, crn):
    """update title attribute from user input"""
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "UPDATE courses "
                stmt_str += "set title = ? "
                stmt_str += "WHERE title = "
                stmt_str += "(SELECT title "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE sections.crn = ?)"
                # stmt_str += "AND courses.courseid = sections.courseid "
                cursor.execute(stmt_str, [user_input, crn])

    except Error as error:
        print(error, file=stderr)
        exit(1)


def update_descrip(user_input, crn):
    """update description attribute from user input"""
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "UPDATE courses "
                stmt_str += "set descrip = ? "
                stmt_str += "WHERE descrip = "

                stmt_str += "(SELECT descrip "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE sections.crn = ? )"

                cursor.execute(stmt_str, [user_input, crn])

    except Error as error:
        print(error, file=stderr)
        exit(1)


def update_prereqs(user_input, crn):
    """update prereqs attribute from user input"""
    try:
        with connect(DATABASE_URL, isolation_level=None,
                     uri=True) as connection:

            with closing(connection.cursor()) as cursor:

                # Create a prepared statement and substitute values.
                stmt_str = "UPDATE courses "
                stmt_str += "set prereqs = ? "
                stmt_str += "WHERE prereqs = "

                stmt_str += "(SELECT prereqs "
                stmt_str += "FROM courses "
                stmt_str += "NATURAL JOIN sections "
                stmt_str += "WHERE sections.crn = ? )"

                cursor.execute(stmt_str, [user_input, crn])

    except Error as error:
        print(error, file=stderr)
        exit(1)
