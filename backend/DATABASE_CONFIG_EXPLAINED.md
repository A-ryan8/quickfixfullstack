# Database Configuration Explained 📖

## How Our Python Application Knows About the Database

You're absolutely right! Our Python application knows about the database through a specific "address book" system. Here's exactly how it works:

## 1. The "Address Book" - The .env File 📖

The most important file is the `.env` file in the backend folder. This file acts as a secure place where we write down the exact address and login details for our database.

**What we place inside `backend/.env`:**

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=civic_db
DB_PORT=3306
```

**Explanation of each line:**
- `DB_HOST=localhost`: Tells the application that the database server is running on the same computer
- `DB_NAME=civic_db`: **This is the direct answer** - we explicitly tell the application that the database name is `civic_db`
- `DB_USER=root`: The MySQL username
- `DB_PASSWORD=your_mysql_password`: The MySQL password
- `DB_PORT=3306`: The port MySQL is running on

## 2. The "Code that Reads the Address Book" - The config.py File 🧑‍💻

The `.env` file just stores the information. The code that actually reads this information is in `backend/config.py`:

```python
# This line loads all the variables from your .env file
load_dotenv()

# This code block uses the loaded variables to connect
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),      # Reads 'localhost' from .env
    'user': os.getenv('DB_USER'),      # Reads 'root' from .env
    'password': os.getenv('DB_PASSWORD'), # Reads your password from .env
    'database': os.getenv('DB_NAME')   # Reads 'civic_db' from .env
}
```

The `os.getenv("DB_NAME")` function is what fetches the name `civic_db` from the `.env` file and passes it to the MySQL connection function.

## 3. The "Connection Manager" - The database.py File 🔌

Finally, `backend/database.py` uses this configuration to actually connect to MySQL:

```python
def get_db_connection():
    db_connection = mysql.connector.connect(**DB_CONFIG)
    # This connects using all the values from DB_CONFIG
```

## Summary: The Complete Flow 🔄

1. **`.env` file** stores: `DB_NAME=civic_db`
2. **`config.py`** reads: `os.getenv('DB_NAME')` → `'civic_db'`
3. **`database.py`** connects: `mysql.connector.connect(database='civic_db')`

This is why our Python application knows to connect to the `civic_db` database - it's explicitly defined in our "address book" (`.env` file) and read by our configuration code!

## Security Note 🔒

The `.env` file contains sensitive information (like passwords) and should never be committed to version control. That's why we have:
- `env_template.txt` - A template without real credentials
- `.env` - The actual file with real credentials (gitignored)
