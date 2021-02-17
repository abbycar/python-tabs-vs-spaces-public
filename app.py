from flask import Flask, render_template, request, Response

app = Flask(__name__)


# @app.before_first_request
# def setup():
# """Initial database and session setup"""


# def init_connection_engine():
# """Set engine configurations and Create SQL Alchemy engine"""


# def init_unix_connection_engine(db_config):
# """Create SQL Alchemy engine for interacting with DB """


@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


# def get_index_context():
# """Tally votes and return vote information"""


# @app.route("/", methods=["POST"])
# def save_vote():
# """Save vote to database"""


# def access_secret_version(secret_version_id):
#     """Return the value of a secret's version"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
