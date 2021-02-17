import datetime

import sqlalchemy
from flask import Flask, render_template, Response, request
from sqlalchemy.orm import sessionmaker

from models import create_database, Votes

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
    context = get_index_context()
    return render_template('index.html', **context)


def get_index_context():
    """Tally votes and return vote information"""
    votes_dict = []

    # Execute the query and fetch all results
    recent_votes = session.query(Votes.candidate, Votes.time_cast).order_by(Votes.time_cast.desc()).limit(5).all()

    for row in recent_votes:
        votes_dict.append({"candidate": row[0], "time_cast": row[1]})

    # Count number of votes for tabs
    tab_count = session.query(Votes).filter(Votes.candidate == "Tabs").count()

    # Count number of votes for spaces
    space_count = session.query(Votes).filter(Votes.candidate == "Spaces").count()
    return {
        'recent_votes': votes_dict,
        'space_count': space_count,
        'tab_count': tab_count,
    }


@app.route("/", methods=["POST"])
def save_vote():
    # Get the team and time the vote was cast.
    team = request.form["team"]
    time_cast = datetime.datetime.utcnow()

    if team != "TABS" and team != "SPACES":
        return Response(response="Invalid team specified.", status=400)

    try:
        session.add(Votes(time_cast=time_cast, candidate=team))
        session.commit()
    except Exception as e:
        return Response(
            status=500,
            response="Unable to successfully cast vote!",
        )
    return Response(
        status=200,
        response="Vote successfully cast for '{}'".format(team),
    )


# def access_secret_version(secret_version_id):
#     """Return the value of a secret's version"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
