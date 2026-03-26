# XJCO2913 - Group 11 - Scooter Hire System
Software Engineering Project - Electric Scooter Hire System

## Project Overview

A **Software Engineering Project** implementing an **Electric Scooter Hire System** built with Django and Python. This system provides a comprehensive platform for managing electric scooter rentals, including user management, scooter inventory, booking management, and administrative controls.

**Language Composition:** Python (70%), HTML (30%)

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Project Structure Details](#project-structure-details)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Functionality

- **User Management**: User registration, authentication, and profile management
- **Scooter Fleet Management**: Track and manage available electric scooters
- **Booking System**: Users can browse available scooters and make reservations
- **Admin Dashboard**: Administrative interface for managing users, scooters, and bookings
- **Rental Tracking**: Real-time tracking of scooter rentals and returns
- **Payment Integration**: Support for rental pricing and payment processing

### Administrative Features

- Complete CRUD operations for scooters and users
- Admin panel for monitoring system activities
- User role-based access control
- Reporting and analytics capabilities

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Backend development language |
| **Django** | Web framework for rapid development |
| **HTML** | Frontend templating and UI |
| **SQLite/PostgreSQL** | Database management |
| **Django ORM** | Database abstraction and modeling |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Littlerunner6/XJCO2913-Group11-ScooterHire.git
   cd XJCO2913-Group11-ScooterHire
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Navigate to project directory**
   ```bash
   cd scooter_project
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

---

## Quick Start

### Running the Development Server

```bash
cd scooter_project
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Admin Access

```bash
# Access the Django admin panel at:
http://127.0.0.1:8000/admin/
```

Use your superuser credentials (created during installation) to log in.

---

## Usage

### For Users

1. **Register/Login**: Create an account or log in to the system
2. **Browse Scooters**: View available electric scooters
3. **Make a Booking**: Reserve a scooter for your desired time period
4. **Track Rental**: Monitor your active rental in real-time
5. **Manage Account**: Update profile information and view booking history

### For Administrators

1. **Access Admin Panel**: Log in with admin credentials
2. **Manage Users**: Add, edit, or remove user accounts
3. **Manage Scooters**: Add new scooters to the fleet or update existing ones
4. **Monitor Bookings**: View and manage all active and historical bookings
5. **Generate Reports**: Analyze usage patterns and system statistics

---

## Project Structure Details

```
XJCO2913-Group11-ScooterHire/
├── scooter_project/                # Main Django project directory
│   ├── scooter/                    # Main Django app
│   │   ├── admin.py                # Django admin configuration
│   │   ├── apps.py                 # App configuration
│   │   ├── models.py               # Database models (Scooter, Booking, User, etc.)
│   │   ├── views.py                # View logic for rendering pages
│   │   ├── urls.py                 # URL routing configuration
│   │   ├── tests.py                # Unit tests
│   │   ├── migrations/             # Database migration files
│   │   └── templates/              # HTML templates
│   │
│   ├── scooter_project/            # Project settings directory
│   │   ├── settings.py             # Django project settings
│   │   ├── urls.py                 # Main URL configuration
│   │   ├── wsgi.py                 # WSGI application entry point
│   │   └── asgi.py                 # ASGI application entry point
│   │
│   ├── manage.py                   # Django management command utility
│   └── admin.txt                   # Admin account credentials (keep secure)
│
└── README.md                       # This file
```

### Key Files Explanation

| File | Purpose |
|------|---------|
| `models.py` | Defines database schemas for Scooters, Users, Bookings, and Payments |
| `views.py` | Contains business logic and request handlers |
| `urls.py` | Maps URL patterns to view functions |
| `admin.py` | Configures Django admin interface |
| `settings.py` | Django configuration (database, installed apps, middleware) |
| `manage.py` | Entry point for Django management commands |

---

## Database Models

### Core Models

- **User**: Extends Django's built-in user model with additional fields
- **Scooter**: Represents individual scooters with status and location info
- **Booking**: Records rental transactions and user bookings
- **Payment**: Manages payment records and transaction history
- **Location**: Tracks docking stations and scooter locations

---

## API Endpoints

### Main Routes

- `GET /` - Home page
- `GET /scooters/` - List all available scooters
- `GET /scooters/<id>/` - View scooter details
- `POST /bookings/` - Create a new booking
- `GET /bookings/` - View user's bookings
- `GET /admin/` - Admin panel

---

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Django Shell (Interactive Console)

```bash
python manage.py shell
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'django'`
- **Solution**: Ensure virtual environment is activated and dependencies are installed: `pip install -r requirements.txt`

**Issue**: Database migration errors
- **Solution**: Reset migrations: `python manage.py migrate --fake-initial`

**Issue**: Admin credentials not working
- **Solution**: Create a new superuser: `python manage.py createsuperuser`

---

## License

This project is part of the XJCO2913 Software Engineering course at Leeds.

**Academic Use Only**

---

## Acknowledgments

- Django Framework documentation and community
- Course instructors and mentors
- All team members who contributed to this project

---

**Last Updated**: March 2026

**Project Status**: ✅ Active Development