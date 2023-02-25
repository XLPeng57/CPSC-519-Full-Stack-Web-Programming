"""Module that generates html web pages
"""
from time import strftime
from flask import Flask, request, make_response, redirect
from flask import render_template, abort
import database
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

# -----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')
auth = HTTPBasicAuth()
user_id = ""

# -----------------------------------------------------------------------

# this is where user/password is stored for now, need to retrieve from database later
# database.add_user("yixuan","nfls")
# admin|jerryu11
# customer|password123
user_data = database.get_users()
users = {}
for user in user_data:
    users[user[0]] = generate_password_hash(user[1])


@auth.verify_password
def verify_password(username, password):
    """Verify the username and password, modified from penny example"""
    if username in users and check_password_hash(users.get(username), password):
        global user_id
        user_id = username
        return username


@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)


def get_ampm():
    """Get am or pm postfix for current time"""
    if strftime('%p') == "AM":
        return 'morning'
    return 'afternoon'


def get_current_time():
    """Return the formatted current time"""
    return strftime("%Y-%m-%d %I:%M %p")


def get_recommendation():
    global user_id

    query_result = database.get_recommend(user_id)
    # query_result = database.get_principal_cast(query_result)
    likes = database.get_liked(user_id)

    html = render_template('searchform.html',
                           ampm=get_ampm(),
                           course_result=[],
                           query_result=query_result,
                           likes=likes,
                           current_time=get_current_time())
    response = make_response(html)
    response.set_cookie("Rec", "yes")
    return response

# -----------------------------------------------------------------------


@app.route('/', methods=['GET', 'POST'])
@app.route('/log_in', methods=['GET'])
def log_in():
    """log in page"""

    html = render_template('log_in.html',
                           ampm=get_ampm(),
                           current_time=get_current_time())
    response = make_response(html)
    return response


@app.route('/search', methods=['GET', 'POST'])
@auth.login_required
def search_form():
    """Generate the page containing the result table of courses"""

    if request.method == "POST":
        media_id = request.form['media_id']
        media_type = request.form['media_type']
        print(media_id)
        genre = request.form['genre']
        database.like_unlike(user_id, media_id, media_type, genre)

    if request.args.get("Recommendation") is not None:
        response = get_recommendation()
        return response

    # print(request.cookies.get('Rec'))
    # if request.cookies.get('Rec'):
    #     response = get_recommendation()
    #     return response

        # if request.args.get("searchMovie") is None and request.args.get("use_cookie") is None:
        #     response = get_recommendation()
        #     return response

    if request.args.get("use_cookie"):
        rating_input = request.cookies.get("Rating")
        if (rating_input is None or rating_input == ''):
            rating_input = ''
        type_input = request.cookies.get("Type")
        if (type_input is None or type_input == ''):
            type_input = ''
        else:
            type_input = type_input.upper()
        title_input = request.cookies.get("Title")
        if (title_input is None or title_input == ''):
            title_input = ''
        else:
            title_input = title_input.upper()
    else:
        rating_input = request.args.get("Rating")
        if (rating_input is None or rating_input == ''):
            rating_input = ''
        type_input = request.args.get("Type")
        if (type_input is None or type_input == ''):
            type_input = ''
        else:
            type_input = type_input.upper()
        title_input = request.args.get("Title")
        if (title_input is None or title_input == ''):
            title_input = ''
        else:
            title_input = title_input.upper()

    query_result = database.get_filtered([title_input, type_input, rating_input])

    likes = database.get_liked(user_id)

    print(len(query_result))
    # if len(query_result) > 0:
    #     print(len(query_result))
    # query_result = database.get_principal_cast(query_result)

    html = render_template('searchform.html',
                           ampm=get_ampm(),
                           course_result=[],
                           rating_input=rating_input,
                           type_input=type_input,
                           title_input=title_input,
                           query_result=query_result,
                           likes=likes,
                           current_time=get_current_time())

    response = make_response(html)
    response.set_cookie("Rating", rating_input)
    response.set_cookie("Type", type_input)
    response.set_cookie("Title", title_input)
    return response


@app.route('/review_rating', methods=['GET', 'POST'])
def add_review():
    """Handles user review and ratings"""
    global user_id
    media_id = request.args.get("media_id")
    if media_id is None:
        media_id = request.cookies.get("MediaId")
    media_name = database.get_media_name(media_id)
    if request.args.get("userReview") is not None and request.args.get("userRating") is not None:
        review = request.args.get("userReview")
        rating = request.args.get("userRating")
        try:
            float(rating)
            database.review_rating(user_id, media_id, review, rating)
        except ValueError:
            print("Not a float")

    html = render_template('review_rating.html', 
                            media_id=media_id,
                            media_name=media_name)
    response = make_response(html)
    response.set_cookie("MediaId", media_id)

    return response


@app.route('/addfriend', methods=['GET', 'POST'])
def add_friend():
    """Handles adding friends"""
    global user_id
    if request.method == "POST":
        username = request.form['username']
        database.add_remove_friend(user_id, username)

    username = request.args.get("username")
    if username is None:
        username = request.cookies.get("username")
    if username is None:
        username = ""
    query_result = database.search_friend(user_id, username)

    friends = database.get_friends(user_id)

    html = render_template('addfriend.html',
                           username=username,
                           friends=friends,
                           query_result=query_result)
    response = make_response(html)
    response.set_cookie("username", username)

    return response


@app.route('/createUser', methods=['GET', 'POST'])
def create_user():
    """Handles creating user"""
    global user_id, users
    if request.method == "POST":
        print("!!!!!!!!!!!!!!!!!!!!")
        username = request.form['Username']
        password = request.form['Password']
        database.add_user(username, password)
        user_data = database.get_users()
        for user in user_data:
            users[user[0]] = generate_password_hash(user[1])

    html = render_template('create_user.html')
    response = make_response(html)

    return response


# -----------------------------------------------------------------------


# @app.route('/details', methods=['GET', 'POST'])
# def get_crn_details():
#     """Generate the details after the user clicks a crn"""
#     if request.method == "POST":
#         text = request.form['text']
#         field = request.args.get("field")
#         database.edit_field(request.args.get("crn"), field, text)

#     crn = request.args.get('crn', None)
#     if not crn:
#         abort(400, "Error: missing crn in details request")

#     crn_exists = database.check_crn_exists(crn)
#     if not crn_exists:
#         abort(404, "Error: no class with crn " + str(crn) + " exists")

#     deptinfo, title, description, prereqs, sections, crosslistings, profs = database.search_crn(
#         crn)
#     html = render_template('details.html',
#                            deptinfo=deptinfo,
#                            title=title,
#                            description=description,
#                            prereqs=prereqs,
#                            sections=sections,
#                            crosslistings=crosslistings,
#                            profs=profs,
#                            crn=crn)
#     response = make_response(html)
#     response.set_cookie("title", title)
#     response.set_cookie("prereqs", prereqs)
#     response.set_cookie("description", description)
#     return response


# @app.route('/edit_details', methods=['GET', 'POST'])
# def edit_crn_details():
#     """Generate the page for the user to edit specific fields in database"""
#     crn = request.args.get('crn', None)
#     field = request.args.get('field', None)
#     info = ""
#     if field == "title":
#         info = request.cookies.get("title")
#     elif field == "description":
#         field = "descrip"
#         info = request.cookies.get("description")
#     elif field == "prereqs":
#         info = request.cookies.get("prereqs")
#     print("info is " + info)
#     html = render_template(
#         'editdetails.html', details=info, crn=crn, field=field)
#     response = make_response(html)
#     return response

# # -----------------------------------------------------------------------


# @app.errorhandler(400)
# def custom_error_400(error):
#     """400 Error"""
#     return render_template('400.html', error_msg=error.description), 400


# @app.errorhandler(404)
# def custom_error(error):
#     """404 Error"""
#     return render_template('404.html', error_msg=error.description), 404
