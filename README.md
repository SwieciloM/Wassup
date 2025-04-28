<h1 align="center">Wassup
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

Wassup is a real-time web chat application built using django for educational purposes. Users can register, log in, create public or private chat rooms, and exchange text and photo messages asynchronously via WebSockets. With room management, message history, and secure file access, this app offers a modern, interactive messaging experience for small communities or private groups.

<div align="center">
    <img src="https://github.com/user-attachments/assets/example-chat-preview.gif" width="640" height="360" />
</div>

---

## 🚀 Features

- 🔐 User authentication with registration and login
- 🗨️ Real-time messaging with text and photo support
- 🔒 Private and public chat rooms with role-based access
- ⭐ Favorite rooms and join/leave functionality
- 🛡️ Secure file access (only authorized users can view images)
- 📑 Recent message previews and sorted room lists

---

## 🛠️ Technologies Used

- **Backend**: Django, Django Channels, Daphne, Redis (prod)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Other**: WhiteNoise, django-environ, django-select2

---

## 🧪 Local Installation (Windows)

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

## 📱 Usage

1. Register a new account or log in.
2. Create or join a public/private chat room.
3. Start messaging in real-time!
4. Favorite or leave rooms at any time.

<div align="center"> <img src="https://github.com/user-attachments/assets/demo-chat-ui.png" width="350" height="300" /> </div>

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
