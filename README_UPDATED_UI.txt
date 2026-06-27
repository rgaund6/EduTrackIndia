EduConnect Palghar - Updated UI Build

What was updated:
- Modern CollegeDekho-inspired (original) home page
- Premium login/register/OTP pages
- Dashboard redesign with Boisar Directory, metrics, quick actions
- Modern institute directory, college search, detail, exams, notifications, saved colleges, analytics, profile and recommendation pages
- Shared base layout and main CSS added/updated

Run:
1. python -m venv venv
2. venv\Scripts\activate
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py load_boisar_data
6. python manage.py runserver

Open:
http://127.0.0.1:8000/
