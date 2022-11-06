1. Create a new folder with the {folder_name}.
2. Open in VS Code and open the CMD inside it.
3. Check for python and git versions. (Install Python-3.10 or higher and latest Git version)
4. Excute: git pull "{git repository URL}"
5. cd into the project folder i.e. hikvision.
6. Execute: python manage.py runserver (To create the inital database, SQLite3)
7. Check for a db.sqlite3 file created.
8. Execute: python manage.py makemigrations (To create the database and the table schemas)
9. Execute: python manage.py migrate (To commit to the db.sqlite3 file)
10. Execute: python manage.py runserver (To run the live server)


List of APIs to test on postman and on the browser:
1. localhost (Displays the devices online.)
2. localhost/getusers (Displays the users on devices that are online.)
3. localhost/getCount (Displays the count - face, person, card for online devices.)
4. localhost/addUserTemplate (Create, Read, Update, Delete for user templates.)
5. localhost/blockUsers (To block users using the EmployeeID.)
