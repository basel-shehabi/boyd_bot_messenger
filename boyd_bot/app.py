from flask import request, redirect, render_template
from . import *


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        return redirect("/", code=302)

    if not guard.sanitized([request.headers, request.args], wb_arg_name, webhook_token):
        return redirect("/", code=403)

    request_data = request.get_json()
    sender_id = platform.get_id(request_data)

    if db.check_registered(sender_id):
        response = user_gateway(request_data, sender_id)

    elif db.check_in_reg(sender_id):
        response = (
            "It doesn't seem like you've registered yet.\n"
            "Register here: {}/register?id={}"
        ).format(app_url, db.get_reg_id(sender_id))

    else:
        user_data = platform.get_user_data(sender_id)
        if "error" in user_data and sender_id != "demo":
            return log("{} is not a valid user".format(sender_id))

        reg_id = db.insert_in_reg(sender_id)
        response = (
            "Hey there, {}! I'm Boyd Bot - your university chatbot, here to make things easier. "
            "To get started, register here: {}/register?id={}"
        ).format(user_data.get("first_name", "new person"), app_url, reg_id)

    return platform.reply(response)


@app.route("/register", methods=["GET", "POST"])
def new_user_registration():

    if request.method == "GET":

        if not guard.sanitized(request.args, "id", None, db):
            return redirect("/", code=404)

        reg_id = request.args.get("id")
        return render_template("register.html", form=RegisterForm(reg_id=reg_id))

    else:

        if not guard.sanitized(
            request.form, ["reg_id", "uni_id", "uni_pw", "remember"], None, db
        ):
            return redirect("/", code=400)

        reg_id = request.form.get("reg_id")
        uni_id = request.form.get("uni_id")
        uni_pw = request.form.get("uni_pw")
        remember = request.form.get("remember")

        uid = db.get_user_id(reg_id)
        login_result = timetable.login(uid, uni_id, uni_pw)
        log("{} undergoing registration. Result: {}".format(uid, login_result))

        if not login_result[0]:
            return render_template(
                "register.html",
                form=RegisterForm(reg_id=reg_id),
                message=login_result[1],
            )

        db.delete_data(uid)
        db.delete_data(reg_id)
        user_details = [uni_id, uni_pw] if remember else [None, None]
        db.insert_data(uid, *user_details)
        platform.send_message(uid, reg_acknowledge)

        return render_template("register.html", success=success_msg)


def user_gateway(request_data, uid):

    try:
        user_data = db.get_data(uid)

        if not timetable.check_loggedIn(user_data["_id"]):

            log("{} logging in again.".format(uid))

            if not guard.sanitized(user_data, ["uni_id", "uni_pw"]):
                db.delete_data(uid)
                return one_time_done

            login_result = timetable.login(
                user_data["_id"], user_data["uni_id"], user_data["uni_pw"]
            )

            if not login_result[0]:

                log("{} failed to log in. Result: {}".format(uid, login_result))
                db.delete_data(uid)
                reg_id = db.insert_in_reg(uid)

                return (
                    "Whoops! Something went wrong; maybe your login details changed?\n"
                    "Register here: {}/register?id={}"
                ).format(app_url, reg_id)

        message = parser.parse(request_data, uid)

    except Exception as e:
        log(
            "Exception ({}) thrown: {}. {} requested '{}'.".format(
                type(e).__name__, e, uid, request_data
            )
        )
        message = error_message

    return message


if __name__ == "__main__":
    app.run(debug=True, port=80)
