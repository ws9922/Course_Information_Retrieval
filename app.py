from flask import Flask, request, redirect, render_template
from CourseSeacher import CourseSearcher

app = Flask(__name__, template_folder="front")
searcher = CourseSearcher()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def searching():
    search_query = request.form['search_query']
    return redirect('/search/' + search_query)

@app.route("/search/<search_query>")
def searching_with_query(search_query):

    search_result = [
        {'course_num': 'cs225', 'course_name': 'data structure', 'credits':'5', 'course_description':'abcdefg'},
        {'course_num': 'cs225', 'course_name': 'data structure', 'credits':'5', 'course_description':'abcdefg'},
        {'course_num': 'cs225', 'course_name': 'data structure', 'credits':'5', 'course_description':'abcdefg'}
    ]

    return render_template('results.html', search_result=search_result)

@app.route("/courses/<course_name>")
def course(course_name):
    data = searcher.get_course(course_name)

    course_info = {
        'num': data['title'],
        'name': data['names'],
        'credits': data['credit'],
        'description': data['intro'],
        'prerequisites': ", ".join(data['prereq']),
        'after': 'cs374',
    }

    professors = [prof for prof in data['instructors'] if len(prof) != 0]
    professor_info = searcher.get_prof(professors)
    if professor_info is None:
        professor_info = {"name":"professor rating not found", "comments": ["", "", ""], "tags": [""], "rating": " "}

    professor_info["tags"] = ", ".join(professor_info["tags"][0].split("|"))

    return render_template('course.html', course_info=course_info, professor_info=professor_info)

app.run(port=3000, debug=True)