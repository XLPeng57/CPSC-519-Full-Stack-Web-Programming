class Movie:

    def __init__(self, tconst):

        self._id = tconst
        self._title = None
        self._rating = None
        self._author = None
        self._object_type = None
        self._cast = None
        self._genre = None

    def get_id(self):
        return self._id

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title

    def set_rating(self, rating):
        self._rating = rating

    def get_rating(self):
        return self._rating

    def set_author(self, author):
        self._author = author

    def get_author(self):
        return self._author

    def set_type(self, object_type):
        self._object_type = object_type

    def get_type(self):
        return self._object_type

    def set_genre(self, genre):
        self._genre = genre

    def get_genre(self):
        return self._genre

    def set_cast(self, cast):
        # self._cast += str(cast)
        # self._cast += ", "
        self._cast = cast

    def get_cast(self):
        # if (self._cast == ""):
        #     return self._cast
        return self._cast
