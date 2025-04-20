<h1 align="center">Real-Time Chat App 💬  
<br />
<a href="https://github.com/yourusername/wassup/actions/workflows/django.yml">
    <img src="https://github.com/yourusername/wassup/actions/workflows/django.yml/badge.svg" alt="Build Status"/>
</a>
<a href="https://coveralls.io/github/yourusername/wassup?branch=main">
    <img src="https://coveralls.io/repos/github/yourusername/wassup/badge.svg?branch=main" alt="Coverage Status"/>
</a>
<a href="https://app.codacy.com/gh/yourusername/wassup/dashboard">
    <img src="https://app.codacy.com/project/badge/Grade/yourbadgeid" alt="Codacy Badge"/>
</a>
<a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/>
</a>
<a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Versions"/>
</a>
</h1>

A real-time web-based chat application built with Django and Channels. Users can register, log in, create public or private chat rooms, and exchange text and photo messages asynchronously via WebSockets. With room management, message history, and secure file access, this app offers a modern, interactive messaging experience for small communities or private groups.

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

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/wassup.git
cd wassup

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file with at least:
echo SECRET_KEY=your_secret_key > .env

# 5. Apply migrations
python manage.py migrate

# 6. Start the development server
python manage.py runserver
```
Open the application in your browser at http://127.0.0.1:8000

## 📱 Usage

1. Register a new account or log in.
2. Create or join a public/private chat room.
3. Start messaging in real-time!
4. Favorite or leave rooms at any time.

<div align="center"> <img src="https://github.com/user-attachments/assets/demo-chat-ui.png" width="350" height="300" /> </div>

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
