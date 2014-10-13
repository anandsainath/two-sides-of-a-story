# Import flask and template operators
from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

# Define the WSGI application object
app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "socomp"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t@sK3Y"

db = MongoEngine(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from app.data.controllers import mod_data as mod_data

# Register blueprint(s)
app.register_blueprint(mod_data)