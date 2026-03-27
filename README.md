# Municipality Service Delivery System
## NHCI63110 Assignment – Part C2

### Project Structure
```
municipality_system/          ← Django project root
├── manage.py
├── requirements.txt
├── municipality_system/      ← Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 ← App 1: User auth (login/register)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templates/accounts/
│       ├── login.html
│       └── register.html
└── reports/                  ← App 2: Issue reporting & messaging
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    └── templates/reports/
        ├── base.html
        ├── dashboard.html
        ├── report_form.html
        ├── report_list.html
        ├── report_detail.html
        └── messages.html
```

### Setup Instructions
1. Install Python 3.10+
2. `pip install -r requirements.txt`
3. `python manage.py makemigrations`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`
7. Visit http://127.0.0.1:8000
