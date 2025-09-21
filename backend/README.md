# Backend Setup

This backend is built with Python and FastAPI.

## 1. Create and Activate Virtual Environment

First, create a virtual environment to manage project dependencies. Run these commands from within the `backend` folder.

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

## 2. Install Dependencies

With your virtual environment active, install the necessary Python packages:

**Option 1: Install from requirements.txt (recommended):**
```bash
pip install -r requirements.txt
```

**Option 2: Install packages individually:**
```bash
pip install fastapi "uvicorn[standard]" mysql-connector-python "python-jose[cryptography]"
```

## 3. Database Setup

Before running the server, make sure you have MySQL installed and running.

### Create Environment File

**Option 1: Use the setup script (recommended):**
```bash
python setup_env.py
```

**Option 2: Manual setup:**
1. Copy the template: `cp env_template.txt .env`
2. Edit the `.env` file with your actual MySQL credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=civic_db
DB_PORT=3306
```

**Important:** The `.env` file contains sensitive information and should never be committed to version control.

Create the database and table:
```sql
CREATE DATABASE civic_db;
USE civic_db;

CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    imageUrl VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'New',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Run the Development Server

To start the server, run the following command. The `--reload` flag will automatically restart the server when you make code changes.

```bash
uvicorn main:app --reload
```

The server will be running at `http://localhost:8000`. You can visit `http://localhost:8000/docs` in your browser to see the automatic API documentation.

### Your Next Steps

After Cursor runs the prompt:
1. Follow the instructions in this `README.md` file to set up your virtual environment and install the packages.
2. Run the server using the `uvicorn` command.
3. Open your browser and go to **`http://localhost:8000/docs`**. You should see the FastAPI documentation page, which means your new backend is working!
