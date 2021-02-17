import sqlalchemy
from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker

from models import create_database

app = Flask(__name__)

db = None
session = None


@app.before_first_request
def setup():
    global db
    global session
    db = init_connection_engine()
    create_database(db)

    Session = sessionmaker(bind=db)
    session = Session()


def init_connection_engine():
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    }
    return init_unix_connection_engine(db_config)


def init_unix_connection_engine(db_config):
    db_socket_dir = "/cloudsql"
    cloud_sql_connection_name = "abbycar-project:us-central1:my-instance"

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username="user",
            password="password",
            database="voting_db",
            query={
                "unix_socket": "{}/{}".format(
                    db_socket_dir,
                    cloud_sql_connection_name)
            }
        ),
        **db_config
    )
    return pool


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
