Django Task Manager
A simple task management web application built using Django. It supports user authentication and CRUD operations for tasks.

🚀 Features
User registration & login
Dashboard with task list
Add new task
Edit existing task
Mark task as completed
Mark completed task as pending
Delete task
Logout functionality



📌 URL Routes
Below are the URL paths configured in urls.py:

Path	View Function	Name
/	login_page	login
/login/	do_login	do_login
/register/	do_signup	do_signup
/dashboard/	dashboard_page	dashboard
/add-task/	add_task	add_task
/edit-task/<int:task_id>/	edit_task	edit_task
/complete-task/<int:task_id>/	complete_task	complete_task
/pending-task/<int:task_id>/	pending_task	pending_task
/delete-task/<int:task_id>/	delete_task	delete_task
/logout/	do_logout	logout
📂 Project Setup
Follow these steps to run the project locally:

1. Clone the Repository
git clone
cd

2. Create & Activate Virtual Environment
Create venv: python -m venv venv

Activate venv: Linux/Mac → source venv/bin/activate
Windows → venv\Scripts\activate

3. Install Requirements
pip install -r requirements.txt

4. Apply Migrations
python manage.py makemigrations
python manage.py migrate

5. Run Development Server
python manage.py runserver

Visit: http://127.0.0.1:8000/



🧪 Creating Superuser
python manage.py createsuperuser

Admin Login Page: /admin



📝 Notes
Ensure Django is installed
Add your templates & static files correctly
Views must be defined in views.py
Protect dashboard & task pages with @login_required



👨‍💻 Contribution
Pull requests are welcome!
Feel free to improve this project.



📄 License
This project is open-source. Use it freely for learning and development.
