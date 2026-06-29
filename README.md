<div align="center">
  <img src="static/imgs/Logo/logo8%20sem%20fundo.png" alt="CineVibe logo" width="280"/>

  ### A full-stack movie ticket booking platform built as a final-year capstone project

  [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
  [![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
  [![License](https://img.shields.io/badge/License-Academic-yellow?style=for-the-badge)](#license)

  <br/>

  **[Features](#-features) · [Screenshots](#-screenshots) · [Tech Stack](#-tech-stack) · [Database Schema](#-database-schema) · [Getting Started](#-getting-started) · [Project Structure](#-project-structure)**

</div>

<br/>

## 🎬 About

**CineVibe** is a complete cinema ticket booking system developed as my final-year **PAP (Prova de Aptidão Profissional)** capstone project for 2026. It simulates a real-world movie theater chain platform — from browsing now-showing films and picking seats in a live seat map, to a full admin dashboard for managing movies, cinemas, screening rooms, and bookings.

The goal was to build something close to a production-ready product: a relational database with dozens of interconnected entities, a Flask backend handling authentication and business logic, and a polished, responsive frontend — all without a frontend framework, just HTML, CSS and vanilla JavaScript.

<br/>

## ✨ Features

<table>
<tr>
<td valign="top" width="33%">

### 🌐 Public Area
- Browse now-showing & upcoming movies
- Advanced search & genre filters
- Detailed movie pages (cast, ratings, trailer)
- Cinema & showtime listings
- Themed screenings (Vintage, Romance, Horror)
- Accessibility features (audio description, sign language, subtitles)

</td>
<td valign="top" width="33%">

### 🎟️ User Area
- Interactive seat selection map
- Concession stand ordering (combos, snacks, drinks)
- Loyalty points & rewards system
- Booking history
- Profile & avatar customization

</td>
<td valign="top" width="34%">

### 🛠️ Admin Dashboard
- Real-time statistics dashboard
- Full CRUD for movies, actors & directors
- Cinema, room & showtime management
- Concession stand product management
- User & booking management
- Exportable reports

</td>
</tr>
</table>

<br/>

## 📸 Screenshots

<div align="center">

**Homepage**
<img src="static/imgs/Logo/Captura%20de%20ecr%C3%A3%202026-06-29%20105433.png" alt="CineVibe homepage" width="100%"/>

<br/><br/>

<table>
<tr>
<td width="50%">

**Movie Catalog**
<img src="static/imgs/Logo/Screenshot%202026-06-28%20at%2023-52-03%20Filmes%20-%20CineVibe%20A%20Sua%20Experi%C3%AAncia%20Cinematogr%C3%A1fica.png" alt="Movie catalog with genre filters"/>

</td>
<td width="50%">

**Movie Details**
<img src="static/imgs/Logo/Screenshot%202026-06-28%20at%2023-39-33%20Superman%20-%20CineVibe%20Detalhes%20do%20Filme.png" alt="Movie detail page with cast"/>

</td>
</tr>
<tr>
<td width="50%">

**Ratings & Reviews**
<img src="static/imgs/Logo/Screenshot%202026-06-28%20at%2023-39-55%20Superman%20-%20CineVibe%20Detalhes%20do%20Filme.png" alt="Ratings, IMDb score and user reviews" height="450"/>

</td>
<td width="50%">

**Login**
<img src="static/imgs/Logo/Screenshot%202026-06-29%20at%2009-26-07%20Login%20CineVibe.png" alt="Login page" height="450"/>

</td>
</tr>
</table>

<br/>

**Interactive Seat Selection**
<img src="static/imgs/Logo/Screenshot%202026-06-28%20at%2023-42-06%20Sele%C3%A7%C3%A3o%20de%20Lugares%20CineVibe.png" alt="Interactive seat map" width="100%"/>

<br/><br/>

<table>
<tr>
<td width="50%">

**Admin · Movie Management**
<img src="static/imgs/Logo/Screenshot%202026-06-29%20at%2009-34-51%20Gest%C3%A3o%20de%20Filmes%20-%20CineVibe%20Admin.png" alt="Admin dashboard movie management"/>

</td>
<td width="50%">

**Admin · Room Management**
<img src="static/imgs/Logo/Screenshot%202026-06-29%20at%2009-36-07%20Gest%C3%A3o%20de%20Salas%20-%20CineVibe%20Admin.png" alt="Admin dashboard room management"/>

</td>
</tr>
</table>

</div>

<br/>

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask |
| **Database** | MySQL 8 |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) |
| **Charts** | Chart.js |
| **Icons** | Font Awesome |
| **Fonts** | Google Fonts (Inter, Montserrat, Roboto) |

<br/>

## 🗄️ Database Schema

CineVibe's data model spans 40+ relational tables, covering everything from movies, cinemas, rooms and showtimes to bookings, concession orders, loyalty points, themed sessions and accessibility seating.

<div align="center">
  <img src="static/imgs/Logo/Screenshot%202026-06-29%20at%2010-59-20%20base_de%20dados_conect.pdf.png" alt="CineVibe database ER diagram" width="100%"/>
</div>

<br/>

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- A modern web browser (Chrome, Firefox, Edge)

### 1. Set up the Python environment

```bash
pip install -r requirements.txt
```

### 2. Set up the database

**Create the database**

```sql
CREATE DATABASE cinevibe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Import the data**

Using your preferred MySQL client (MySQL Workbench, DBeaver, etc.), import `cinevibe.sql`:

- **MySQL Workbench** → `File > Run SQL Script` → select `cinevibe.sql`
- **DBeaver** → right-click the database → `Execute SQL Script` → select `cinevibe.sql`
- **Command line:**
  ```bash
  mysql -u root -p cinevibe < cinevibe.sql
  ```

### 3. Configure database credentials

Open `app.py` and locate the `get_db_connection()` function (around line 381), then update it with your MySQL credentials:

```python
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",  # change this
        database="cinevibe"
    )
```

### 4. Run the application

```bash
python app.py
```

The app will be available at **http://127.0.0.1:5000**

### 5. Create an admin account

1. Go to `http://127.0.0.1:5000/registo` and create a user account
2. Promote it to admin via MySQL:
   ```sql
   UPDATE usuarios SET is_admin = TRUE WHERE email = 'your_email@example.com';
   ```
3. Log in and access the admin dashboard at `/admin`

<br/>

## 📁 Project Structure

```
cinevibe/
├── app.py                    # Main Flask application (configure MySQL credentials here)
├── requirements.txt          # Python dependencies
├── cinevibe.sql               # Full database dump
├── static/
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   ├── imgs/                  # Images & assets
│   └── videos/                # Promotional videos
└── templates/                 # HTML templates
```

<br/>

## 🩹 Troubleshooting

<details>
<summary><strong>Database connection error</strong></summary>
<br/>

- Make sure MySQL is running
- Double-check the credentials in `app.py` (`get_db_connection`)
- Confirm the `cinevibe` database was created

</details>

<details>
<summary><strong>Error importing cinevibe.sql</strong></summary>
<br/>

- Verify you have sufficient permissions
- Make sure you're running MySQL 8.0+
- Try importing in smaller chunks if the file is too large

</details>

<details>
<summary><strong>Port 5000 already in use</strong></summary>
<br/>

Change the port at the bottom of `app.py`:

```python
app.run(debug=True, port=5001)
```

</details>

<details>
<summary><strong>Missing Python modules</strong></summary>
<br/>

- Run `pip install -r requirements.txt` again
- Make sure you're using Python 3.8+

</details>

<br/>

## 📄 License

Developed as a **Final Capstone Project (PAP)** — 2026.

<br/>

<div align="center">
  <sub>Built with ☕ and a lot of SQL joins.</sub>
</div>
