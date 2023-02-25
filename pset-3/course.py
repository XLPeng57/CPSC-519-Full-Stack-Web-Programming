"""container classes for sending information to html"""

class Course:
    """container class for sending data to html"""
    def __init__(self, crn, deptname, subjectcode, coursenum, title):
        self._crn = crn
        self._deptname = deptname
        self._subjectcode = subjectcode
        self._coursenum = coursenum
        self._title = title

    def get_crn(self):
        """getter for crn"""
        return self._crn

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


class CourseDetail:
    """container class for sending data to html"""
    def __init__(self, crn):
        self._crn = crn
        self._deptname = None
        self._subjectcode = None
        self._coursenum = None
        self._title = None
        self._descrip = None

        self._prereqs = []
        self._crosslist = []
        self._profs = []
        self._sections = []

    def set_crn(self, crn):
        """setter for crn"""
        self._crn = crn

    def get_crn(self):
        """getter for crn"""
        return self._crn

    def set_deptname(self, deptname):
        """setter for deptname"""
        self._deptname = deptname

    def get_deptname(self):
        """getter for deptname"""
        return self._deptname

    def set_subjectcode(self, subjectcode):
        """setter for subjectcode"""
        self._subjectcode = subjectcode

    def get_subjectcode(self):
        """getter for subjectcode"""
        return self._subjectcode

    def set_coursenum(self, coursenum):
        """setter for coursenum"""
        self._coursenum = coursenum

    def get_coursenum(self):
        """getter for coursenum"""
        return self._coursenum

    def set_title(self, title):
        """setter for title"""
        self._title = title

    def get_title(self):
        """getter for title"""
        return self._title

    def set_descrip(self, descrip):
        """setter for descrip"""
        self._descrip = descrip

    def get_descrip(self):
        """getter for descrip"""
        return self._descrip

    def set_prereqs(self, prereqs):
        """setter for prereqs"""
        self._prereqs.append(prereqs)

    def get_prereqs(self):
        """getter for prereqs"""
        return self._prereqs

    def set_sections(self, section):
        """setter for sections"""
        self._sections.append(section)

    def get_sections(self):
        """getter for sections"""
        return self._sections

    def set_crosslist(self, crosslist):
        """setter for croslist"""
        self._crosslist.append(crosslist)

    def get_crosslist(self):
        """getter for crosslist"""
        return self._crosslist

    def set_profs(self, prof):
        """setter for profs"""
        self._profs.append(prof)

    def get_profs(self):
        """getter for profs"""
        return self._profs
