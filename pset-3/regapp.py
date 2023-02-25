"""handles html interactions"""
from time import localtime, asctime, strftime
from flask import Flask, request, make_response, render_template, abort
import database


app = Flask(__name__, template_folder='.')

class Cookies:
    """a static class to hold html cookies"""

    def __init__(self, deptname, subjectcode, coursenum, title):
        self._is_clear = True
        self._crn = False
        self._deptname = deptname
        self._subjectcode = subjectcode
        self._coursenum = coursenum
        self._title = title

    def set(self, deptname, subjectcode, coursenum, title):
        """setter for all fields of values"""
        self._deptname = deptname
        self._subjectcode = subjectcode
        self._coursenum = coursenum
        self._title = title

    def get_deptname(self):
        """getter for deptname"""
        return self._deptname

    def get_subjectcode(self):
        """getter for subjectcode"""
        return self._subjectcode

    def get_coursenum(self):
        """getter for coursenum"""
        return self._coursenum

    def get_title(self):
        """getter for title"""
        return self._title

    def set_crn(self, crn):
        """setter for boolean value CRN"""
        self._crn = crn

    def from_crn(self):
        """check if user just returned from course detail page"""
        return self._crn

    def set_clear(self):
        """setter for boolean value is_clear"""
        self._is_clear = True

    def is_clear(self):
        """check if the form should be cleared"""
        if self._is_clear:
            self._is_clear = False
            return True
        return False


cookies = Cookies("$", "$", "$", "$")


def get_ampm():
    """get AM/PM string"""
    if strftime('%p') == "AM":
        return 'morning'
    return 'afternoon'


def get_current_time():
    """get current time"""
    return asctime(localtime())


@app.route('/', methods=['GET'])
@app.route('/search', methods=['GET'])
def search_results():
    """handles search page rendering and user interaction"""
    if request.args.get('clear') == "Clear Previous Search" or cookies.is_clear():
        cookies.set_clear()
        cookies.set("", "", "", "")
    else:
        if cookies.from_crn():
            deptname = cookies.get_deptname()
            coursenum = cookies.get_coursenum()
            subjectcode = cookies.get_subjectcode()
            title = cookies.get_title()
        else:
            deptname = request.args.get('deptname')
            coursenum = request.args.get('coursenum')
            subjectcode = request.args.get('subjectcode')
            title = request.args.get('title')

            cookies.set(deptname, subjectcode, coursenum, title)

    cookies.set_crn(False)

    courses = []

    if not cookies.is_clear():
        courses = database.search(cookies.get_deptname(), cookies.get_coursenum(
        ), cookies.get_subjectcode(), cookies.get_title())

    html = render_template('search.html',
                           ampm=get_ampm(),
                           current_time=get_current_time(),
                           deptname=cookies.get_deptname(),
                           coursenum=cookies.get_coursenum(),
                           subjectcode=cookies.get_subjectcode(),
                           title=cookies.get_title(),
                           courses=courses)
    response = make_response(html)

    return response


@app.route('/details', methods=['GET'])
def search_details():
    """handles course detail page rendering and user interaction"""

    cookies.set_crn(True)

    crn = request.args.get('crn')
    if not crn:
        abort(400, "Error: missing crn in details request")

    course_detail = database.search_detail(crn)

    if course_detail.get_coursenum() is None:
        abort(404, "Error: no class with crn " + str(crn) + " exists")

    html = render_template('details.html',
                           ampm=get_ampm(),
                           current_time=get_current_time(),
                           crn=crn,
                           course_detail=course_detail)

    response = make_response(html)
    return response


@app.route('/edit', methods=['GET'])
def edit():
    """handles course detail editing"""
    edit_type = request.args.get('edit_type')
    detail = request.args.get('detail')
    print(detail)
    crn = request.args.get('crn')
    html = render_template('edit.html',
                           ampm=get_ampm(),
                           current_time=get_current_time(),
                           edit_type=edit_type,
                           detail=detail,
                           crn=crn)
    response = make_response(html)
    return response


@app.route('/edit', methods=['GET', 'POST'])
def update_database():
    """handles database update from user editing"""
    edit_type = request.form['edit_type']
    crn = request.form['crn']
    user_input = request.form['userInput']
    print(edit_type)
    print(crn)

    if edit_type == 'Title':
        print(user_input)
        database.update_title(user_input, crn)

    if edit_type == 'Description':
        print(user_input)
        database.update_descrip(user_input, crn)

    if edit_type == 'Prerequisites':
        print(user_input)
        database.update_prereqs(user_input, crn)

    course_detail = database.search_detail(crn)

    return render_template('details.html',
                           ampm=get_ampm(),
                           current_time=get_current_time(),
                           crn=crn,
                           course_detail=course_detail)
