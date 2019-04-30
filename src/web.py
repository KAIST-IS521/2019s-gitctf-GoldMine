# Rename to cert
import cert
import user
from flask import Flask, request, send_file
from waitress import serve


app = Flask(__name__)

def authenticate(request):
    username = request.form["uid"]
    password = request.form["password"]
    record = user.authenticate(username, password)
    return record

@app.route("/", methods=["GET"])
def index():
    return "Hello from GoldMine CA!"

@app.route("/", methods=["POST"])
def get_user():
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        uid = user_record["uid"]
        last_name = user_record['last_name']
        first_name = user_record['first_name']
        email = user_record['email']

        return "ID: {}\nLast Name: {}\nFirst Name: {}\nEmail: {}\n".format(uid, last_name, first_name, email)
    except:
        return "Error occurred while processing the request"

@app.route("/join", methods=["POST"])
def join():
    try:
        form = request.form
        register_data = { k: form[k] for k in user.properties }
        user.register(register_data)
        cert.generate_record(register_data['uid'])
        return "Welcome to GoldMine"
    except:
        return "Error occurred while processing the request"

@app.route("/edit", methods=["POST"])
def edit_user():
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        uid = user_record["uid"]
        form = request.form
        new_data = { k: form[k] for k in (set(form.keys()) & user.properties - { "uid", "password" }) }
        if "new_password" in form:
            new_data["password"] = form["new_password"]
        user.edit(uid, new_data)
        return "Your information was changed successfully"
    except:
        return "Error occurred while processing the request"

@app.route("/upload-key", methods=["POST"])
def upload_key():
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        uid = user_record["uid"]
        key_data = request.form["key"]
        cert.upload_key(uid, key_data)
        return "Your key is registered successfully."
    except:
        return "Error occurred while processing the request"

@app.route("/fetch/<username>", methods=["POST"])
def fetch_cert(username):
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        return cert.download_cert(username)
    except:
        return "Error occurred while processing the request"

@app.route("/crl", methods=["GET"])
def crl():
    try:
        return cert.download_crl()
    except:
        return "Error occurred while processing the request"

@app.route("/revoke/<fingerprint>", methods=["POST"])
def revoke_key(fingerprint):
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        uid = user_record["uid"]
        cert.revoke_key(uid, fingerprint)
        return "Your key with the given fingerprint is now revoked. Please update your services with another certificate."
    except:
        return "Error occurred while processing the request"

@app.route("/validate", methods=["POST"])
def validate_certificate():
    try:
        certificate = request.form["certificate"]
        return str(cert.is_valid_certificate(certificate))
    except:
        return "Error occurred while processing the request"

@app.route("/edit/image", methods=["POST"])
def edit_user_image():
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        uid = user_record["uid"]
        reset_image = "default" in request.form
        image_file = request.files["image"]
        image = None if reset_image else image_file.read()
        user.edit_image(uid, image)
        return "Your user image is successfully set!"
    except:
        return "Error occurred while processing the request"

@app.route("/image", methods=["POST"])
def get_user_image():
    try:
        user_record = authenticate(request)
        if not user_record:
            return "Invalid username or password"

        uid = user_record["uid"]
        return send_file(str(user.get_image_path(uid)), mimetype="image/png")
    except:
        return "Error occurred while processing the request"

if __name__ == "__main__":
    cert.initialize()
    serve(app, host="0.0.0.0", port=80)
