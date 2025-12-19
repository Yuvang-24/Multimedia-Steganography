from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os, datetime

from config import Config
from modules.image_steg.encoder import encode as img_encode
from modules.image_steg.decoder import decode as img_decode
from modules.audio_steg.encoder import encode as aud_encode
from modules.audio_steg.decoder import decode as aud_decode
from modules.video_steg.encoder import encode as vid_encode
from modules.video_steg.decoder import decode as vid_decode

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("instance", exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------------- DATABASE ----------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    module = db.Column(db.String(20))
    action = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

def save_history(module, action, filename):
    record = History(
        username=current_user.username,
        module=module,
        action=action,
        filename=filename
    )
    db.session.add(record)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    history = History.query.filter_by(
        username=current_user.username
    ).order_by(History.time.desc()).all()
    return render_template("dashboard.html", history=history)


# ---------------- IMAGE ----------------
@app.route("/image", methods=["GET", "POST"])
@login_required
def image():
    if request.method == "POST":
        mode = request.form.get("mode")
        img = request.files.get("carrier")

        if not img:
            flash("Please upload an image", "warning")
            return redirect(url_for("image"))

        in_path = os.path.join(app.config["UPLOAD_FOLDER"], img.filename)
        img.save(in_path)

        # -------- ENCODE --------
        if mode == "encode":
            secret = request.form.get("secret", "").strip()
            if not secret:
                flash("Please enter secret text", "warning")
                return redirect(url_for("image"))

            out_path = in_path.rsplit(".", 1)[0] + "_stego.png"
            img_encode(in_path, secret, out_path)

            save_history("Image", "Encode", os.path.basename(out_path))

            return send_from_directory(
                app.config["UPLOAD_FOLDER"],
                os.path.basename(out_path),
                as_attachment=True
            )

        # -------- DECODE --------
        else:
            try:
                decoded_text = img_decode(in_path)

                # ✅ SAVE TO TXT FILE
                txt_filename = "decoded_image.txt"
                txt_path = os.path.join(app.config["UPLOAD_FOLDER"], txt_filename)

                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(decoded_text)

                save_history("Image", "Decode", os.path.basename(in_path))

                return send_from_directory(
                    app.config["UPLOAD_FOLDER"],
                    txt_filename,
                    as_attachment=True
                )

            except Exception as e:
                flash("No hidden text found or image corrupted", "danger")
                return redirect(url_for("image"))

    return render_template("image.html")



# ---------------- AUDIO ----------------
@app.route("/audio", methods=["GET", "POST"])
@login_required
def audio():
    if request.method == "POST":
        mode = request.form.get("mode")
        wav = request.files.get("carrier")

        if not wav:
            flash("Please upload a WAV file", "warning")
            return redirect(url_for("audio"))

        in_path = os.path.join(app.config["UPLOAD_FOLDER"], wav.filename)
        wav.save(in_path)

        # -------- ENCODE --------
        if mode == "encode":
            secret = request.form.get("secret", "").strip()
            if not secret:
                flash("Please enter secret text", "warning")
                return redirect(url_for("audio"))

            out_path = in_path.replace(".wav", "_stego.wav")
            aud_encode(in_path, secret, out_path)

            save_history("Audio", "Encode", os.path.basename(out_path))
            return send_from_directory(
                app.config["UPLOAD_FOLDER"],
                os.path.basename(out_path),
                as_attachment=True
            )

        # -------- DECODE --------
        else:
            out_path = in_path.replace(".wav", "_decoded.txt")
            aud_decode(in_path, out_path)

            save_history("Audio", "Decode", os.path.basename(in_path))
            return send_from_directory(
                app.config["UPLOAD_FOLDER"],
                os.path.basename(out_path),
                as_attachment=True
            )

    return render_template("audio.html")

# ---------------- VIDEO ----------------
@app.route("/video", methods=["GET", "POST"])
@login_required
def video():
    if request.method == "POST":
        mode = request.form.get("mode")
        video = request.files.get("carrier")

        if not video:
            flash("Please upload a video", "warning")
            return redirect(url_for("video"))

        v_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
        video.save(v_path)

        if mode == "encode":
            secret_text = request.form.get("secret_text", "").strip()
            secret_file = request.files.get("secret_file")

            if secret_text:
                payload_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    f"video_secret_{int(datetime.datetime.now().timestamp())}.txt"
                )
                with open(payload_path, "w", encoding="utf-8") as f:
                    f.write(secret_text)

            elif secret_file and secret_file.filename:
                payload_path = os.path.join(app.config["UPLOAD_FOLDER"], secret_file.filename)
                secret_file.save(payload_path)

            else:
                flash("Provide secret text or file", "warning")
                return redirect(url_for("video"))

            out_path = v_path.rsplit(".", 1)[0] + "_stego.mkv"
            vid_encode(v_path, payload_path, out_path)

            save_history("Video", "Encode", os.path.basename(out_path))

            return send_from_directory(
                app.config["UPLOAD_FOLDER"],
                os.path.basename(out_path),
                as_attachment=True
            )

        else:  # decode
            try:
               extracted_file = vid_decode(v_path, app.config["UPLOAD_FOLDER"])
               save_history("Video", "Decode", os.path.basename(v_path))
               return send_from_directory(
                   app.config["UPLOAD_FOLDER"],
                   os.path.basename(extracted_file),
                   as_attachment=True
                )
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("video"))

    return render_template("video.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
