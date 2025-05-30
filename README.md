<h1 align="center">Wassup
    <img src="https://github.com/user-attachments/assets/c99e75d7-1426-41d8-b30b-e83fcc256e4a" alt="Chat icon" width="24" height="24">
    <br />
    <a href="https://github.com/SwieciloM/Wassup/actions/workflows/django.yml">
        <img src="https://github.com/SwieciloM/Wassup/actions/workflows/django.yml/badge.svg" alt="Build Status"/>
    </a>
    <a href="https://coveralls.io/github/SwieciloM/Wassup?branch=master">
        <img src="https://coveralls.io/repos/github/SwieciloM/Wassup/badge.svg?branch=master" alt="Coverage Status"/>
    </a>
    <a href="https://app.codacy.com/gh/yourusername/wassup/dashboard">
        <img src="https://app.codacy.com/project/badge/Grade/c3e457752e13403aa0db183bdd05a063" alt="Codacy Badge"/>
    </a>
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/>
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python Versions"/>
    </a>
</h1>

Wassup is a real-time web chat application built with Django for educational purposes. The project aims to provide a straightforward platform for small- and medium-sized groups to communicate without unnecessary add-ons. After logging in, users access a dashboard that lists rooms in three categories: rooms they own, rooms in which they are guests, and public rooms that can be joined at any time. Within any room, participants can exchange text or photo messages in real time, and the full conversation history remains available at all times. Room owners can edit settings, hand ownership to another member, or delete the room. Participants may edit settings if owner allows it, leave room or mark it as a favourite for quick access. These live interactions are delivered over WebSocket connections managed by Django Channels, so updates reach every client immediately without page reloads and with minimal network overhead.

<div align="center">
    <img src="https://github.com/user-attachments/assets/b5cf71df-b803-435c-a79b-839638cc2c3c" width="715" height="423" />
    <img src="https://github.com/user-attachments/assets/97795bc9-7a8c-40ea-a7eb-c89f2ad8354d" width="715" height="382" />
</div>

## Features

- User authentication with registration and login
- Public and private chat rooms with role-based access
- Real-time text and image messaging
- Persistent message history for each room
- Option to mark rooms as favourites
- Secure data access (only authorised members can view messages and images)

## Technologies Used

- **Backend**: Django, Django Channels, Daphne, Redis (prod)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Other**: WhiteNoise, django-environ, django-select2

## Local Installation (Windows)

1. Clone the repository
    ```bash
    git clone https://github.com/SwieciloM/Wassup.git
    cd Wassup
    ```
2. Create and activate a virtual environment
   ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
3. Install dependencies
   ```bash
    pip install -r requirements.txt
   ```
4. Create a .env file with at least:
   ```bash
    echo SECRET_KEY=your_secret_key > .env
   ```
5. Apply migrations to set up the database
   ```bash
    python manage.py migrate
   ```
6. Start the development server
   ```bash
    python manage.py runserver
    ```
7. Open the application in your browser at http://127.0.0.1:8000

## Usage

1. Register a new account or log in.
2. Create or join a public chat room.
3. Start messaging in real-time!
4. Favorite or leave rooms at any time.

<div align="center"> 
    <img src="https://github.com/user-attachments/assets/c6af4f27-9764-4dce-998b-b36af01d3167" width="950" height="475" />
</div>

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
