from app import create_app
from . import db
import os

app = create_app()

with app.app_context():
    db.create_all()  # This creates tables if they don't exist

if __name__ == '__main__':
    app.run(debug=True)