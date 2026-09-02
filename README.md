# 📚 BookScout — Backend API

The backend API for **BookScout**, an AI-powered book discovery and personal library management platform.

BookScout's backend is built with **Python and Flask** and provides secure user authentication, personal library management, database persistence, and AI-powered features for personalized book recommendations and reading analytics.

---

## ✨ Features

-  **JWT Authentication** — Secure user registration, login, and protected API routes.
-  **Password Hashing** — User passwords are securely hashed using Flask-Bcrypt.
-  **Personal Library Management** — Users can add, update, and remove books from their personal library.
-  **Reading Status Tracking** — Track books using statuses such as `Want to Read`, `Reading`, and `Read`.
-  **Book Ratings** — Users can rate books using star ratings.
-  **AI Recommendations** — Gemini AI generates personalized book recommendations based on user requests and library history.
-  **Reading DNA** — Gemini analyzes a user's rated books to generate a personalized reading profile.
-  **User-Owned Data** — Library records are associated with individual users.
-  **Rate Limiting** — AI recommendation requests are limited to prevent excessive API usage.
-  **Health Check** — A dedicated endpoint reports API and AI service status.
-  **Database Support** — SQLite for development and PostgreSQL for production.
-  **RESTful API** — Structured endpoints for authentication, library management, and AI functionality.

---

##  Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Backend programming language |
| **Flask 2.3.2** | REST API framework |
| **Flask-SQLAlchemy 3.0.5** | Database ORM |
| **Flask-JWT-Extended 4.5.2** | JWT authentication |
| **Flask-Bcrypt 1.0.1** | Password hashing |
| **Flask-CORS 4.0.0** | Cross-Origin Resource Sharing |
| **Google GenAI SDK** | Gemini AI integration |
| **Gemini 3.6 Flash** | AI recommendations and Reading DNA |
| **SQLite** | Local development database |
| **PostgreSQL** | Production database |
| **Gunicorn 21.2.0** | Production WSGI server |
| **Requests 2.31.0** | HTTP requests and API communication |
| **Marshmallow 3.19.0** | Data serialization and validation |
| **python-dotenv 1.0.0** | Environment variable management |

---

##  Architecture

BookScout follows a RESTful client-server architecture. The React frontend communicates with the Flask API using HTTP requests and JSON data.

```text
┌─────────────────────┐
│   React Frontend    │
│                     │
│  Book Discovery     │
│  Personal Library   │
│  AI Features        │
└──────────┬──────────┘
           │
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│    Flask Backend    │
│                     │
│  Authentication     │
│  Library CRUD       │
│  JWT Authorization  │
│  AI Services        │
└───────┬───────┬─────┘
        │       │
        │       │
        ▼       ▼
┌────────────┐ ┌─────────────────┐
│ Database   │ │   Gemini AI     │
│            │ │                 │
│ SQLite /   │ │ Recommendations │
│ PostgreSQL │ │ Reading DNA     │
└────────────┘ └─────────────────┘
````

---

##  Database Model

BookScout uses two primary database models:

### 1. User

Stores registered user accounts.

| Field           | Type     | Description                |
| --------------- | -------- | -------------------------- |
| `id`            | Integer  | Primary key                |
| `username`      | String   | Unique username            |
| `email`         | String   | Unique email address       |
| `password_hash` | String   | Securely hashed password   |
| `created_at`    | DateTime | Account creation timestamp |

### 2. ReadingBook

Stores books saved to a user's personal library.

| Field            | Type     | Description                                                |
| ---------------- | -------- | ---------------------------------------------------------- |
| `id`             | Integer  | Primary key                                                |
| `user_id`        | Integer  | Foreign key referencing `users.id`                         |
| `openlibrary_id` | String   | Open Library book identifier                               |
| `title`          | String   | Book title                                                 |
| `author`         | String   | Book author                                                |
| `cover_url`      | String   | Book cover image URL                                       |
| `status`         | String   | Current reading status (`Want to Read`, `Reading`, `Read`) |
| `rating`         | Integer  | User's star rating (1–5)                                   |
| `created_at`     | DateTime | Record creation timestamp                                  |
| `updated_at`     | DateTime | Last update timestamp                                      |

### Relationship

A user can have multiple books in their personal library, creating a **one-to-many (`1:N`) relationship**.

```text
User
 │
 │ 1
 │
 ▼
Many ReadingBook records
```

---

##  API Endpoints

###  Authentication

| Method | Endpoint        | Description                               | Access       |
| ------ | --------------- | ----------------------------------------- | ------------ |
| `POST` | `/api/register` | Create a new user account                 | Public       |
| `POST` | `/api/login`    | Authenticate a user and issue a JWT       | Public       |
| `GET`  | `/api/me`       | Retrieve the authenticated user's profile | 🔒 Protected |

###  Library Management

| Method   | Endpoint          | Description                       | Access       |
| -------- | ----------------- | --------------------------------- | ------------ |
| `GET`    | `/api/books`      | Retrieve the current user's books | 🔒 Protected |
| `POST`   | `/api/books`      | Add a book to the user's library  | 🔒 Protected |
| `PATCH`  | `/api/books/<id>` | Update reading status or rating   | 🔒 Protected |
| `DELETE` | `/api/books/<id>` | Remove a book from the library    | 🔒 Protected |

###  AI Features

| Method | Endpoint               | Description                                 | Access       |
| ------ | ---------------------- | ------------------------------------------- | ------------ |
| `GET`  | `/api/reading-dna`     | Generate a personalized Reading DNA profile | 🔒 Protected |
| `POST` | `/api/recommendations` | Generate personalized book recommendations  | 🔒 Protected |

###  Health Check

| Method | Endpoint      | Description                          | Access |
| ------ | ------------- | ------------------------------------ | ------ |
| `GET`  | `/api/health` | Check API health and AI availability | Public |

### Example Health Check Response

```json
{
  "status": "healthy",
  "ai_enabled": true
}
```

---

##  AI Integration

BookScout uses Google's **Gemini 3.6 Flash** model to provide personalized reading features.

The Google GenAI SDK is initialized using the Gemini API key stored in the environment.

### Gemini Request

```python
response = ai_client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)
```

The backend requests structured JSON responses from Gemini so that the AI output can be easily consumed by the React frontend.

---

###  AI Recommendations

The `/api/recommendations` endpoint accepts a user's natural-language request.

For example:

```json
{
  "prompt": "I want something like The Silent Patient, but darker and faster paced."
}
```

The backend combines the user's request with their existing library context and sends the information to Gemini.

The API returns structured recommendations:

```json
{
  "recommendations": [
    {
      "title": "Example Book",
      "author": "Example Author",
      "match_percentage": 92,
      "reason": "Matches the requested dark and fast-paced psychological thriller style."
    }
  ]
}
```

### Rate Limiting

AI recommendation requests are limited to:

**5 requests per 60 seconds**

If the limit is exceeded, the API returns HTTP status `429`:

```json
{
  "error": "Rate limit exceeded. Try again in a minute."
}
```

---

### 🧬 Reading DNA

The `/api/reading-dna` endpoint evaluates the user's rated books and sends the information to Gemini to analyze their reading preferences.

The AI generates reading traits with percentage matches.

Example response:

```json
{
  "traits": [
    {
      "name": "Psychological Thriller",
      "percentage": 92
    },
    {
      "name": "Mystery",
      "percentage": 85
    }
  ]
}
```

If a user has no rated books, the API returns a message asking them to add rated books before generating their Reading DNA.

---

## 🔒 Authentication & Password Security

### JWT Authentication

Authenticated routes require a valid JWT passed through the `Authorization` header.

Example:

```http
Authorization: Bearer <JWT_TOKEN>
```

The authentication flow is:

```text
User Registration
       ↓
User Login
       ↓
JWT Token Generated
       ↓
Frontend Stores Token
       ↓
Token Sent With Protected Requests
       ↓
Flask Verifies JWT
       ↓
User Accesses Their Resources
```

### Password Hashing

Passwords are never stored in plain text.

BookScout uses **Flask-Bcrypt** to securely hash passwords before they are stored in the database.

```python
self.password_hash = bcrypt.generate_password_hash(
    password
).decode('utf-8')
```

---

## 📁 Project Structure

```text
bookscout-backend/
│
├── app.py              # Main Flask application
├── config.py           # Application configuration
├── models.py           # SQLAlchemy User and ReadingBook models
├── requirements.txt    # Python dependencies
├── .env                # Local environment variables
├── .gitignore          # Git exclusion rules
│
├── routes/
│   ├── __init__.py
│   ├── auth.py         # Registration, login, and profile routes
│   └── books.py        # Personal library CRUD routes
│
└── venv/               # Python virtual environment
```

---

##  Getting Started

### Prerequisites

Before running the backend, make sure you have:

* Python **3.10 or higher**
* `pip`
* `git`
* A Gemini API key from [Google AI Studio](https://aistudio.google.com/)  (Make sure you use your personal email for this.Do not use school email)

---

### 1. Clone the Repository

```bash
git clone https://github.com/Amos-44/bookscout-backend.git
cd bookscout-backend
```

---

### 2. Create and Activate a Virtual Environment

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Environment Variables

Create a `.env` file in the root directory of the project.

```env
FLASK_APP=app.py
FLASK_ENV=development

SECRET_KEY=your_super_secret_flask_key
JWT_SECRET_KEY=your_super_secret_jwt_key

DATABASE_URL=sqlite:///app.db

GEMINI_API_KEY=your_gemini_api_key_here
```

### Environment Variable Reference

| Variable         | Description                        |
| ---------------- | ---------------------------------- |
| `FLASK_APP`      | Flask application entry point      |
| `FLASK_ENV`      | Flask environment                  |
| `SECRET_KEY`     | Secret key used by Flask           |
| `JWT_SECRET_KEY` | Secret key used to sign JWT tokens |
| `DATABASE_URL`   | Database connection string         |
| `GEMINI_API_KEY` | Google Gemini API key              |

>  **Security Warning:** Never commit your `.env` file or API keys to GitHub. Make sure `.env` is included in `.gitignore`.

---

## 🗄️ Database Setup

Initialize the database tables using:

```bash
python -c "from app import db, app; app.app_context().push(); db.create_all()"
```

For local development, SQLite can be used:

```env
DATABASE_URL=sqlite:///app.db
```

For production, configure PostgreSQL using the appropriate database connection string:

```env
DATABASE_URL=your_postgresql_connection_string
```

---

##  Running Locally

Start the Flask development server:

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

The application listens on:

```text
http://0.0.0.0:5000
```

---

##  API Health Check

After starting the server, check whether the backend is running:

```bash
curl http://127.0.0.1:5000/api/health
```

Example response:

```json
{
  "status": "healthy",
  "ai_enabled": true
}
```

The `ai_enabled` property indicates whether the Gemini AI client was successfully initialized.

---

##  API Testing

The API can be tested using:

* [Postman](https://www.postman.com/)
* [Insomnia](https://insomnia.rest/)
* Thunder Client
* cURL
* The BookScout React frontend

### Example Protected Request

```http
GET /api/books
Authorization: Bearer <JWT_TOKEN>
```

---

## 🌐 Deployment

The backend is designed for deployment on WSGI-compatible hosting platforms such as:

* Render
* Railway

### Production WSGI Command

Gunicorn is used as the production WSGI server:

```bash
gunicorn app:app
```

### Production Environment Variables

Configure the following environment variables through your hosting provider's environment settings:

```text
SECRET_KEY
JWT_SECRET_KEY
DATABASE_URL
GEMINI_API_KEY
```

> Never hard-code production secrets in the source code.

---

## API Response Format

BookScout uses JSON for communication between the frontend and backend.

### Successful Response

Example:

```json
{
  "status": "healthy",
  "ai_enabled": true
}
```

### Error Response

Example:

```json
{
  "error": "Prompt required"
}
```

HTTP status codes are used to indicate the result of API requests, including:

| Status Code | Meaning                            |
| ----------- | ---------------------------------- |
| `200`       | Request successful                 |
| `201`       | Resource created                   |
| `400`       | Bad request                        |
| `401`       | Authentication required or invalid |
| `404`       | Resource not found                 |
| `429`       | Rate limit exceeded                |
| `500`       | Internal server error              |

---

## 🔐 Security

BookScout implements several security measures:

* JWT-based authentication
* Password hashing with Flask-Bcrypt
* Protected API endpoints
* User-specific library records
* Environment variables for sensitive credentials
* CORS configuration
* Rate limiting for AI recommendations

User library records are associated with their authenticated user account through a foreign key relationship.



## Author

**Amos Kiplangat**

### BookScout

> **Discover books. Build your library. Understand your reading.**
