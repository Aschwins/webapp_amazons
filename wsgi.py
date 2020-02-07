from amazons import app, db
from amazons.models import User, Game


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Game': Game}
