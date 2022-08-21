from flask import Flask

from api.v1 import auth_blueprint
from db import db
from settings import PostgresConnection


app = Flask(__name__)
app.register_blueprint(auth_blueprint)
app.config.from_object(PostgresConnection())
db.init_app(app)
app.app_context().push()
db.create_all()


@app.route('/api/hello-world')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
