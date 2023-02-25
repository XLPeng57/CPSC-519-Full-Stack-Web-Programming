""" Module containing interactions with SQL database
"""
#!/usr/bin/env python3

from sqlite3 import connect
from contextlib import closing
from sys import stderr, exit
from movie import Movie

# -----------------------------------------------------------------------

_DATABASE_URL = 'file:imdb.sqlite?mode=rw'

def get_media_name(media_id):
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT primaryTitle "
                query_str += "FROM title_basics "
                query_str += "WHERE tconst = ? "
                

                cursor.execute(query_str, [media_id])
                row = cursor.fetchone()
                if row is not None:
                    return str(row[0])
                else:
                    return ""

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def get_users():
    results = []
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT * "
                query_str += "FROM user_info;"

                cursor.execute(query_str)
                row = cursor.fetchone()
                while row is not None:
                    results.append([str(row[0]), str(row[1])])
                    row = cursor.fetchone()
                return results

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def add_user(user_id, username):

    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "INSERT INTO user_info(user_id, password) VALUES(?, ?);"
                cursor.execute(query_str, [user_id, username])

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def get_friends(user_id):
    results = []
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT friend "
                query_str += "FROM user_friend "
                query_str += "WHERE user_id = ?;"

                cursor.execute(query_str, [user_id])

                row = cursor.fetchone()
                while row is not None:
                    results.append(str(row[0]))
                    row = cursor.fetchone()
                return results

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def search_friend(user_id, username):
    results = []
    if username == "":
        return results
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT user_id "
                query_str += "FROM user_info "
                query_str += "WHERE user_id like ? "
                query_str += "ORDER BY user_id ASC "
                query_str += "LIMIT 50;"

                cursor.execute(query_str, ['%'+username+'%'])

                row = cursor.fetchone()
                while row is not None:
                    if row[0] != user_id:
                        result = str(row[0])
                        results.append(result)
                    row = cursor.fetchone()
                return results

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def add_remove_friend(user_id, username):

    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT friend "
                query_str += "FROM user_friend "
                query_str += "WHERE user_id = ? AND friend = ?;"

                cursor.execute(query_str, [user_id, username])

                row = cursor.fetchone()

                if row is not None:
                    query_str = "DELETE FROM user_friend "
                    query_str += "WHERE user_id = ? "
                    query_str += "and friend = ? ;"
                    cursor.execute(query_str, [user_id, username])

                    query_str = "DELETE FROM user_friend "
                    query_str += "WHERE user_id = ? "
                    query_str += "and friend = ? ;"
                    cursor.execute(query_str, [username, user_id])
                else:
                    query_str = "INSERT INTO user_friend(user_id, friend) VALUES(?, ?);"
                    cursor.execute(query_str, [user_id, username])

                    query_str = "INSERT INTO user_friend(user_id, friend) VALUES(?, ?);"
                    cursor.execute(query_str, [username, user_id])

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def get_liked(user_id):

    results = set()

    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT DISTINCT media_id "
                query_str += "FROM user_liked "
                query_str += "WHERE user_id = ? ;"

                cursor.execute(query_str, [user_id])

                row = cursor.fetchone()
                while row is not None:
                    results.add(str(row[0]))
                    row = cursor.fetchone()

                return results

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def like_unlike(user_id, media_id, media_type, genre):
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT COUNT(*) "
                query_str += "FROM user_liked "
                query_str += "WHERE user_id = ? "
                query_str += "and media_id = ? ;"

                cursor.execute(query_str, [user_id, media_id])
                row = cursor.fetchone()
                res = 0

                while row is not None:
                    res = int(row[0])
                    row = cursor.fetchone()

                if res == 0:
                    query_str = "INSERT INTO user_liked(user_id, media_id, media_type, genre)"
                    query_str += "VALUES(?, ?, ?, ?);"
                    cursor.execute(
                        query_str, [user_id, media_id, media_type, genre])

                else:
                    query_str = "DELETE FROM user_liked "
                    query_str += "WHERE user_id = ? "
                    query_str += "and media_id = ? ;"

                    cursor.execute(query_str, [user_id, media_id])

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def review_rating(user, id, review, rating):
    """Update database with user review and rating.
        *user: username.
        *id: media id.
        *review: user review.
        *rating: user rating.
    """
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "INSERT INTO user_review(user_id, media_id, review, rating) VALUES('"
                query_str += user + "', '"
                query_str += id + "', '"
                query_str += review + "', '"
                query_str += rating + "');"

                cursor.execute(query_str)

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def get_recommend(inputarr):
    """Use the web input to perform SQL search. Returns a list of rows.
        *inputarr: username.
        *courses: a list of recommended rows to be returned
    """
    results = []
    genre = set()
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:

                query_str = "SELECT genre "
                query_str += "FROM user_liked "
                query_str += "WHERE user_id = '"
                query_str += inputarr + "' ;"

                cursor.execute(query_str)

                row = cursor.fetchone()
                while row is not None:
                    genre.add(row[0])
                    row = cursor.fetchone()

    except IndexError:
        print("index error", file=stderr)
        exit(1)

    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                if len(genre) != 0 and genre != set(["None"]):
                    query_str = "SELECT tconst, primaryTitle, titleType, averageRating "
                    query_str += "FROM title_basics "
                    query_str += "NATURAL JOIN title_ratings "
                    query_str += "WHERE "
                    for i in genre:
                        query_str += "genres = '"
                        query_str += i + "' OR "
                    query_str = query_str[:-4]
                    query_str += "ORDER BY averageRating DESC, primaryTitle ASC "
                    query_str += "LIMIT 50;"

                    cursor.execute(query_str)

                    row = cursor.fetchone()
                    while row is not None:
                        result = Movie(str(row[0]))
                        result.set_title(str(row[1]))
                        result.set_type(str(row[2]))
                        result.set_rating(str(row[3]))
                        results.append(result)
                        row = cursor.fetchone()
                else:
                    query_str = "SELECT tconst, primaryTitle, titleType, averageRating "
                    query_str += "FROM title_basics "
                    query_str += "NATURAL JOIN title_ratings "
                    query_str += "ORDER BY averageRating DESC, primaryTitle ASC "
                    query_str += "LIMIT 50;"
                    cursor.execute(query_str)

                    row = cursor.fetchone()
                    while row is not None:
                        result = Movie(str(row[0]))
                        result.set_title(str(row[1]))
                        result.set_type(str(row[2]))
                        result.set_rating(str(row[3]))
                        results.append(result)
                        row = cursor.fetchone()
                return results

    except IndexError:
        print("index error", file=stderr)
        exit(1)


def get_filtered(inputarr):
    """Use the command line input to perform SQL search. Returns a list of rows.
        *inputarr: either conditions or TRUE.
        *courses: a list of rows to be returned
    """
    results = []
    try:
        with connect(_DATABASE_URL, isolation_level=None,
                     uri=True) as connection:
            with closing(connection.cursor()) as cursor:
                query_str = "SELECT tconst, primaryTitle, titleType, averageRating, genres, names "
                query_str += "FROM title_basics "
                query_str += "NATURAL JOIN title_ratings "
                query_str += "NATURAL JOIN (SELECT tconst, GROUP_CONCAT(primaryName, ' | ') as names from name_basics "
                query_str += "NATURAL JOIN title_principals GROUP BY tconst) "
                query_str += "WHERE primaryTitle like ? "
                query_str += "AND titleType like ? "
                query_str += "AND averageRating >= ? "
                query_str += "ORDER BY primaryTitle ASC, averageRating DESC "
                query_str += "LIMIT 100;"

                cursor.execute(query_str, ['%'+inputarr[0]+'%', '%'+inputarr[1]+'%',
                                           inputarr[2]])

                row = cursor.fetchone()
                while row is not None:
                    result = Movie(str(row[0]))
                    result.set_title(str(row[1]))
                    result.set_type(str(row[2]))
                    result.set_rating(str(row[3]))
                    result.set_genre(str(row[4]))
                    result.set_cast(str(row[5]))
                    results.append(result)
                    row = cursor.fetchone()
                return results

    except IndexError:
        print("index error", file=stderr)
        exit(1)


# def get_principal_cast(results):

#     for result in results:
#         try:
#             with connect(_DATABASE_URL, isolation_level=None,
#                          uri=True) as connection:
#                 with closing(connection.cursor()) as cursor:

#                     # use this tconst(identifier) to find top 5 principal casts
#                     tconst = result.get_id()

#                     query_str = "SELECT primaryName "
#                     query_str += "FROM name_basics "
#                     query_str += "NATURAL JOIN title_principals "
#                     query_str += "WHERE tconst = ? "
#                     query_str += "ORDER BY primaryName ASC "
#                     query_str += "LIMIT 3; "

#                     cursor.execute(query_str, [tconst])

#                     cast = ""
#                     row = cursor.fetchone()
#                     while row is not None:
#                         cast += str(row[0]) + ", "
#                         row = cursor.fetchone()
#                     # print(cast)
#                     cast = cast[:-2]
#                     result.set_cast(cast)

#         except IndexError:
#             print("index error", file=stderr)
#             exit(1)

#     return results
