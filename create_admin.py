"""Admin credentials are configured in the .env file (no extra database table)."""
from pathlib import Path
print("CarePoint HMS admin login is configured through .env.")
print("Set ADMIN_USERNAME and ADMIN_PASSWORD in .env, then restart the Flask app.")
print("No app_user table or database migration is required.")
