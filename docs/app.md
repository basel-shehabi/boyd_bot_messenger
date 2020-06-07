# [app.py](https://github.com/ineshbose/boyd_bot_messenger/blob/master/app.py)

This script is the Flask app. It is the only script to have access to the keys and enables webhook.

```python
# App URL as variable to easily change it
app_url = os.environ["APP_URL"]

# Flask Secret Key to enable FlaskForm
app.config['SECRET_KEY'] = os.environ["FLASK_KEY"]

# Webhook Token for GET request
webhook_token = os.environ["VERIFY_TOKEN"]

# Webhook Argument Name
wb_arg_name = os.environ["WB_ARG_NAME"]

# Facebook Page Access Token to use Send/Graph API
facebook = Facebook(os.environ["PAGE_ACCESS_TOKEN"])

# MongoDB data
db = Mongo(os.environ["MONGO_TOKEN"], os.environ["FIRST_CLUSTER"],
            os.environ["COLLECTION_NAME"], os.environ["WAIT_ID"])

# Initialize class Dialogflow
df = Dialogflow()

# Encryption key using Fernet
f = Fernet(os.environ["FERNET_KEY"])
```

## Packages Used
* [flask](https://github.com/pallets/flask)
* [flask_wtf](https://github.com/lepture/flask-wtf)
* [wtforms](https://github.com/wtforms/wtforms)
* [cryptography](https://github.com/pyca/cryptography)


## `RegisterForm()`
```python
class RegisterForm(FlaskForm):
    """Registration form for users.

    Contains 3 essential input fields (+ 1 `SubmitField`).
    """
    fb_id = HiddenField('fb_id')
    uni_id = StringField('University ID', validators=[DataRequired()])
    uni_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
```


## `index()`
```python
@app.route('/')
def index():
    """Returns index() view for the app.

    Returns
    -------
    template
        The home page for the app corresponding the URL (`app_url`+'/').
    """
    return render_template('index.html')
```



## `webhook()`
```python
@app.route('/webhook', methods=['POST'])
def webhook():
    """Enables webhook for the app.

    A method to handle POST requests with the app from Dialogflow.
    GET requests can be added if required.
    
    Returns
    -------
    json
        The response to POST request.
    """

    # This is to enable authorisation of POST requests
    if not request.headers.get(wb_arg_name) == webhook_token:
        return "Verification token mismatch", 403

    data = request.get_json()
    sender_id = data['keys-to-unique-id']
    # rest of the code
    return prepare_json(response)
```



## `new_user_registration()`
```python
@app.route('/register', methods=['GET', 'POST'])
def new_user_registration():
    """Registration for a new user.

    Using `wait_id`, in-registration user is distinguished and then logged in using `timetable.login()` and depending
    on returned boolean value, the page is re-rendered.

    Returns
    -------
    template
        Depending on login, the page is rendered again.
    """
    
    if request.method == "GET":
        # render template if URL argument found in database
    else:
        # try login
        facebook.send_message(fb_id, "Alrighty! We can get started. :D")    # To alert user on Facebook Messenger. This can be removed.
        return
```



## `prepare_json()`
```python
def prepare_json(message):
    """Prepares a formatted JSON containing the message.

    To return a message from a POST request, Dialogflow requires a formatted JSON.
    Using `pymessenger` to send messages would not be good practice.

    Parameters
    ----------
    message : str
        The message to return.

    Returns
    -------
    json
        A formatted JSON for Dialogflow with the message.
    """

    res = { 'fulfillmentText': message, }
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
```



## `handle_intent()`
```python
def handle_intent(data, r):
    """Checks intent for a message and creates response.

    If an intent is found in a message, a response is returned.
    Put all intents handled by the app here.

    Parameters
    ----------
    data :
        The JSON of the POST request.
    r :
        The details of the user on Mongo.

    Returns
    -------
    str
        The response if intent is satisfied

    null
        If intent is not handled by the app, Dialogflow creates response.
    """

    try:
        # if intent1: return something
        # elif intent2: return something else
        # else:
        return
    except:
        # return exception message
```



## `parse_message()`
```python
def parse_message(data, uid):
    """Parses the message of the user.

    The main method handling log in and intents for the message.

    Parameters
    ----------
    data :
        The JSON of the POST request.
    uid : str
        The unique ID for the Facebook user of the app.

    Returns
    -------
    str
        A response for the message.

    null
        If intent is not handled by app, the response is created by Dialogflow.
    """
   
    if not timetable.check_loggedIn(r['uni_id']):
        # login
    
        if not login_result:
            # login failed
    
    return handle_intent(data, r)
```



## `log()`
```python
def log(message):
    """Logs details onto the terminal of server.

    This function can be changed to how logging is intended.

    Parameters
    ----------
    message : str
        The message to log.
    """
    print(message)          # print() is not good practice. Will be replaced.
```