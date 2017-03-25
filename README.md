# A api to upload and view csvs with image links.

This api allows you to upload an csv with links to images. The images will be cached on the server for further downloading.

This is a Python 3.5 app, and has not been tested with any other versions of Python.

## Installing

Below is the basic installation instructions for developping on the app.

The app uses a Postgresql database and it is assumed this is installed and running. It is also assumed that the `pg_hba.conf` file is set as to allow local database users to connect over IPv4 using a md5 password.

Clone repository:

    $ git clone https://github.com/inytar/elements_assignment.git
    $ cd elements_assignment

Create a virtual environment and activate:

    $ pyvenv .venv
    $ source .venv/bin/activate

Install dependencies:

    $ pip install -r requirements.txt

Create new database and database user:

    $ sudo -u postgres psql -c "CREATE USER elements WITH PASSWORD 'elements'"
    $ sudo -u postgres psql -c "CREATE DATBASE elements OWNER elements"

Run the migrations

    $ python manage.py migrate

# Running

To run the application in development:

    $ python manage.py runserver

# Deploying

TODO add a simple docker file for deployment, allow setting config settings throug file or env.



# Limitations
It is not possible to search through the csv files. This could be solved by instead of saving the csv files to disk saving a representation of the files in a Postgres JSONB column.

As we allow uploading files we are vulnerable to: <https://docs.djangoproject.com/en/1.10/topics/security/#user-uploaded-content>. To migate this problem the plan is to implent a basic authentication scheme so that only admins can upload a new csv file.

It is not possible to add, delete or edit a row in a csv file, if a csv file has beeen edited it must be uploaded again.
