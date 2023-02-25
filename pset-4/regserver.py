from sys import stderr, exit
import os
import socket
import argparse
import requests
import pandas as pd
import table
from codes import DEPARTMENTS, SCHOOLS


DATABASE_URL = "reg.sqlite"
df = pd.DataFrame(columns=['crn', 'deptname', 'subject',
                  'num', 'title', 'descrip', 'prereqs',
                           'deptcode', 'profs', 'XL', 'meeting_time',
                           'meeting_location', 'section'])


def get_request(subject_code, school):

    params = {'apikey': 'xxx',
              'subjectCode': subject_code, 'school': school}
    response = requests.get(
        'https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index', params=params)

    if response.status_code != 200:
        return

    result = response.json()

    if len(result) == 0:
        return

    for course in result:

        if course["department"] in DEPARTMENTS:
            department_name = DEPARTMENTS[course["department"]] + \
                '(' + course["department"] + ')'
        else:
            department_name = "None"

        info = [course["crn"], department_name, course["subjectCode"],
                course["courseNumber"], course["courseTitle"],
                course["description"], course["prerequisites"], course["department"], tuple(
                    course["instructorList"]),
                tuple([course["primXLst"]]+course["scndXLst"]
                      ), ", ".join(course['meetingPattern']) + " @",
                ", ".join(course['meetingPatternLocation']), course['sectionNumber']]
        df.loc[len(df)] = info


def generate_course_table(line):
    """
    get statement string and get data from database
    """

    dept = ""
    title = ""
    coursenum = ""
    subject = ""

    if line.find("dept:") != -1:
        i = line.find("dept:") + 5

        while (line[i+1]) != "#" or (line[i+2]) != "#":
            dept += line[i]
            i += 1
        dept += line[i]

    if line.find("coursenum:") != -1:
        i = line.find("coursenum:") + 10
        while (line[i+1]) != "#" or (line[i+2]) != "#":
            coursenum += line[i]
            i += 1
        coursenum += line[i]

    if line.find("subject:") != -1:
        i = line.find("subject:") + 8
        while (line[i+1]) != "#" or (line[i+2]) != "#":
            subject += line[i]
            i += 1
        subject += line[i]

    if line.find("title:") != -1:
        i = line.find("title:") + 6

        while (line[i+1]) != "#" or (line[i+2]) != "#":
            title += line[i]
            i += 1
        title += line[i]

    if dept == "":
        row_dept = df
    else:
        row_dept = df.loc[df['deptname'].str.contains(dept, case=False)]

    if title == "":
        row_title = df
    else:
        row_title = df.loc[df['title'].str.contains(title, case=False)]

    if coursenum == "":
        row_coursenum = df
    else:
        row_coursenum = df.loc[df['num'].str.contains(coursenum, case=False)]

    if subject == "":
        row_subject = df
    else:
        row_subject = df.loc[df['subject'].str.contains(subject, case=False)]

    rows = pd.merge(row_dept, row_title, how='inner')
    rows = pd.merge(rows, row_coursenum, how='inner')
    rows = pd.merge(rows, row_subject, how='inner')
    rows.sort_values(by=['deptname', 'subject', 'num', 'title', 'crn'], ascending=[
                     True, True, True, True, True])
    rows = rows[['crn', 'deptname', 'subject', 'num', 'title']]
    rows = rows.values.tolist()

    if len(rows) == 0:
        print("No results.")
        return ""

    data = [list(r) for r in rows]

    for _, row in enumerate(data):
        row[2] = str(row[2])
        row[4] = str(row[4])

    columns = ['crn', 'deptname', 'subject', 'num', 'title']
    course_table = table.Table(columns, data, max_width=500)

    return str(course_table)


def output(col, data):
    """
    generate a table with given colomn headers and data
    """
    my_table = table.Table(col, data)
    return str(my_table)


def generate_detail_table(course_crn):
    """ generate course detail table """

    course = df.loc[df['crn'].str.match(course_crn)]

    course_info = course[['deptcode', 'deptname', 'subject', 'num']]
    course_info = course_info.values.tolist()

    meeting_info = course[['section', 'meeting_time', 'meeting_location']]
    meeting_info = meeting_info.values.tolist()

    course_title = course[['title']]
    course_title = course_title.values.tolist()

    course_descrip = course[['descrip']]
    course_descrip = course_descrip.values.tolist()

    course_prereqs = course[['prereqs']]
    course_prereqs = course_prereqs.values.tolist()

    course_profs = course['profs'].values.tolist()
    profs = [[str(item)] for item in course_profs[0]]

    course_xl = course['XL'].values.tolist()
    course_xl = [[str(item)] for item in course_xl[0]]

    result = str(output(["deptcode", "deptname", "subjectcode",
                         "coursenum"], course_info)) + "\n\n"
    result += str(output(["title"], course_title)) + "\n\n"
    result += str(output(["descrip"], course_descrip)) + "\n\n"
    result += str(output(["prereqs"], course_prereqs)) + "\n\n"

    result += str(output(["professors"], profs)) + "\n\n"
    result += str(output(["crosslistings"], course_xl)) + "\n\n"
    result += str(output(["section", "time", "location"],
                  meeting_info)) + "\n\n"

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
    for department in DEPARTMENTS:
        for school in SCHOOLS:
            get_request(department, school)
        print("total:" + str(len(df)))

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
