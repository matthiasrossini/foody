os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "foody\\gcp-keys.json"
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{SQL_PASSWORD}@{SQL_PUBLIC_IP}/{SQL_DATABASE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True