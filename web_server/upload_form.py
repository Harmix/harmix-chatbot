from flask import Blueprint, render_template, request, redirect, url_for

upload_form_page = Blueprint('upload_form', __name__, template_folder='templates')

@upload_form_page.route("/upload_form", methods=["GET", "POST"])
def upload_video():
    if request.method == "POST":
        print(request.form)
        user_id = request.form.get("user_id")
        if request.form.get("video_uploads"):
            return redirect(url_for('upload_form.thanks'))

        else:
            error = 'send only video'
            return render_template('upload_form.html', error=error)

    return render_template("upload_form.html")


@upload_form_page.route("/thanks_form", methods=['GET'])
def thanks_form():
    return render_template("thanks_form.html")