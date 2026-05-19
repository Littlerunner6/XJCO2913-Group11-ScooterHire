# XJCO2913 Group 11 - Scooter Hire System

Electric Scooter Hire System for the XJCO2913 Software Engineering coursework.

The application is a Django web app for browsing scooters, creating bookings, simulating payments, managing cards, handling fault feedback, and supporting staff/admin workflows.

## Features

### Customer Features

- Register, log in, and log out using Django authentication.
- Browse available scooters with price, minimum hire period, location, image, and performance information.
- View scooter locations on an interactive Leaflet/OpenStreetMap map.
- Create scooter bookings and receive confirmation email notifications.
- Pay for unpaid bookings with simulated payment flow.
- View, extend, and cancel unpaid bookings.
- Manage saved bank cards, including default card selection.
- Submit scooter fault feedback and view personal feedback history.
- Switch between English and Simplified Chinese.
- Display membership groups in the welcome header for `Student`, `Elderly`, and `FrequentUser` users.

### Staff Features

- Create bookings for unregistered customers with guest name and email.
- Review and filter fault feedback by priority and status.
- Update feedback priority and resolution status.

### Admin Features

- Manage scooters and orders through Django Admin.
- Configure scooter availability, hourly price, minimum hire hours, image, performance text, address, latitude, and longitude.
- View weekly income reports grouped by hire period and day.

## Technology Stack

| Area | Technology |
| --- | --- |
| Backend | Python, Django |
| Database | PostgreSQL |
| ORM | Django ORM |
| Frontend | Django templates, HTML, CSS, JavaScript |
| Map | Leaflet with OpenStreetMap tiles |
| Media | Django media uploads, Pillow |
| Email | Django SMTP email backend |
| Internationalization | Django i18n, `locale/` message files |

## Project Structure

```text
XJCO2913-Group11-ScooterHire/
├── README.md
├── scooter_project/
│   ├── manage.py
│   ├── admin.txt
│   ├── locale/
│   │   ├── en/LC_MESSAGES/
│   │   └── zh_Hans/LC_MESSAGES/
│   ├── media/
│   ├── scooter/
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/scooter/
│   │   │   ├── css/
│   │   │   └── js/
│   │   └── templates/
│   │       ├── admin/
│   │       ├── card/
│   │       ├── feedback/
│   │       ├── order/
│   │       ├── registration/
│   │       ├── staff/
│   │       ├── base.html
│   │       └── index.html
│   ├── scooter_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── staticfiles/
```

## Main Models

- `Scooter`: scooter inventory, pricing, availability, location, image, and performance descriptions.
- `Order`: booking records for registered users and staff-created guest bookings.
- `Card`: saved card metadata for users.
- `Feedback`: fault reports with status and priority.
- `User`: Django built-in user model, with membership handled through Django groups.

## Key Routes

| Route | Purpose |
| --- | --- |
| `/` | Home page, available scooters, active unpaid orders, map |
| `/login/` | Login |
| `/logout/` | Logout |
| `/register/` | Register |
| `/order/create/<scooter_id>/` | Booking form for one scooter |
| `/order/submit/` | Submit booking form |
| `/order/pay/<order_id>/` | Simulated payment |
| `/order/my/` | Current user's orders |
| `/order/cancel/<order_id>/` | Cancel unpaid order |
| `/order/extend/<order_id>/` | Extend unpaid booking |
| `/card/list/` | Saved cards |
| `/card/add/` | Add card |
| `/staff/create-booking/` | Staff booking for guest customers |
| `/feedback/create/` | Submit scooter fault feedback |
| `/feedback/my/` | User feedback history |
| `/feedback/list/` | Staff feedback management |
| `/feedback/update/<feedback_id>/` | Staff feedback update |
| `/income/weekly/` | Admin weekly income report |
| `/admin/` | Django Admin |
| `/i18n/` | Django language switching |

## Setup

### Prerequisites

- Python 3.9 or later
- PostgreSQL running locally
- A virtual environment

The current local environment uses:

```text
Django==4.2.29
psycopg2-binary==2.9.11
Pillow==11.3.0
```

There is currently no `requirements.txt` in the repository. Install the required packages manually:

```bash
python -m venv venv
source venv/bin/activate
pip install Django==4.2.29 psycopg2-binary==2.9.11 Pillow==11.3.0
```

### Database

The current `settings.py` expects this PostgreSQL database:

```text
ENGINE: django.db.backends.postgresql
NAME: scooter_db
USER: postgres
PASSWORD: 123456
HOST: localhost
PORT: 5432
```

Create the database before migrating:

```bash
createdb scooter_db
```

If your local PostgreSQL credentials differ, update `scooter_project/scooter_project/settings.py`.

### Migrate and Create Admin User

```bash
cd scooter_project
python manage.py migrate
python manage.py createsuperuser
```

### Run the Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## Development Commands

Run Django system checks:

```bash
python manage.py check
```

Run tests:

```bash
python manage.py test scooter
```

Create migrations after model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

Compile translation messages after editing `.po` files:

```bash
python manage.py compilemessages
```

Collect static files:

```bash
python manage.py collectstatic
```

## User Groups and Discounts

The app uses Django groups for membership-specific behavior:

| Group | Discount |
| --- | --- |
| `FrequentUser` | 20% off |
| `Elderly` | 15% off |
| `Student` | 10% off |

If a user belongs to multiple groups, the application applies the first match in this priority order:

```text
FrequentUser -> Elderly -> Student
```

These groups are also displayed in the home page welcome header.

## Notes for Demonstration

- Add scooters in Django Admin before demonstrating booking.
- Set valid `address`, `latitude`, and `longitude` values so the map markers render correctly.
- Mark scooters as available to make them visible on the home page.
- Give staff accounts `is_staff=True` to access staff booking and feedback management.
- Give admin accounts `is_superuser=True` to access weekly income and Django Admin.
- Assign users to `Student`, `Elderly`, or `FrequentUser` groups to demonstrate discount and membership display.

## Security Notes

This is coursework/demo code and is not production-ready as-is.

- `SECRET_KEY`, database credentials, and email credentials are currently hard-coded in `settings.py`.
- Move secrets to environment variables before deployment.
- Do not commit real SMTP passwords or production credentials.
- `DEBUG=True` is enabled and should be disabled for production.
- `ALLOWED_HOSTS` is empty and should be configured for deployment.

## Troubleshooting

### `ModuleNotFoundError: No module named 'django'`

Activate the virtual environment and install dependencies:

```bash
source venv/bin/activate
pip install Django==4.2.29 psycopg2-binary==2.9.11 Pillow==11.3.0
```

### PostgreSQL Connection Error

Confirm PostgreSQL is running and that `scooter_db` exists. Then verify the credentials in `settings.py`.

### No Scooters on Home Page

Create scooters in Django Admin and make sure `is_available=True`.

### Map Shows Default Location

Set real latitude and longitude values for scooters in Django Admin.

## License

This project is part of the XJCO2913 Software Engineering course at Leeds.

Academic use only.
