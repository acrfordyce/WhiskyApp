# WhiskyApp

To set up environment:

Set up a virtualenv so that WhiskyApp/bin/python exists.
WhiskyApp/bin/pip install -r requirements.txt

Next run db_create.py to create app.db and associated files.
Changes to the schema can be incorporated by using db_upgrade.py when required.
To wipe the db and start fresh, delete app.db and the db_repository directory and then run db_create.py again.

To start the app, use run.py and navigate to localhost:5000 in a browser.

