import datetime
from flask import Flask, render_template, Response, request
from sqlalchemy.orm import sessionmaker

from models import create_database, Votes

app = Flask(__name__)
session_fact = None


@app.before_first_request
def before_first_request():
    global session_fact

    db = init_connection_engine()
    session_fact = sessionmaker(bind=db)
    create_database(db)


# Set db connection config. Return configured db connection
def init_connection_engine():
    db_config = {
        # Max number of permanent connections
        "pool_size": 5,
        # Max connections allowed in overflow
        "max_overflow": 2,
        # Max number of seconds to wait when retrieving a new connection
        "pool_timeout": 30,
        # Max number of seconds a connection can persist before reestablishing
        "pool_recycle": 1800,
    }
    return init_unix_connection_engine(db_config)


# Creates database engine via unix socket connection
def init_unix_connection_engine(db_config):
    # Cloud SQL instance's Unix domain socket accessed on the environment's filesystem
    db_socket_dir = "/cloudsql"
    cloud_sql_connection_name = "abbycar-project:us-central1:my-instance"

    # Create SQLAlchemy engine
    pool = create_engine(URL(
        drivername='mysql+pymysql',
        username="user",
        password="password",
        database='voting_db',
        query={
            "unix_socket": f"{db_socket_dir}/{cloud_sql_connection_name}"
        }
    ), **db_config)
    return pool


# Access the value of a specified secret version
def access_secret_version(secret_version_id):
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_version_id)

    return response.payload.data.decode('UTF-8')


# Render webpage
@app.route("/", methods=["GET"])
def index():
    context = get_index_context()
    return render_template('index.html', **context)


@contextmanager
def session_scope():
    session = session_fact()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Get voting context
def get_index_context():
    """Tally votes and return vote information"""
    votes_dict = []

    with session_scope() as session:
        # Query most recent 5 votes
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


# Save votes to db
@app.route("/", methods=["POST"])
def save_vote():
    # Get the team and time the vote was cast.
    team = request.form["team"]
    time_cast = datetime.datetime.utcnow()

    if team != "TABS" and team != "SPACES":
        return Response(response="Invalid team specified.", status=400)

    try:
        with session_scope() as session:
            session.add(Votes(time_cast=time_cast, candidate=team))
    except Exception as e:
        return Response(
            status=500,
            response="Unable to successfully cast vote!",
        )
    return Response(
        status=200,
        response="Vote successfully cast for '{}'".format(team),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
