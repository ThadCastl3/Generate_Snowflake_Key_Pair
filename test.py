import snowflake.connector
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import getpass

load_dotenv()


# --- Get User Input for Key Details ---
SNOWFLAKE_USER = input("Enter the Snowflake username used for key generation: ")
PRIVATE_KEY_PASSPHRASE = getpass.getpass("Enter the passphrase for the private key: ")
key_directory_input = input("Enter the directory where keys were saved (leave blank for ./keys): ")
KEY_DIRECTORY = key_directory_input if key_directory_input else "./keys"

PRIVATE_KEY_FILE = os.path.join(KEY_DIRECTORY, f"{SNOWFLAKE_USER}_key.pem")

# --- Connection Configuration ---
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

# --- Read and Deserialize Private Key ---
try:
    print(f"Attempting to read private key from: {os.path.abspath(PRIVATE_KEY_FILE)}")
    with open(PRIVATE_KEY_FILE, "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=PRIVATE_KEY_PASSPHRASE.encode() if PRIVATE_KEY_PASSPHRASE else None,
            backend=default_backend(),
        )

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
except FileNotFoundError:
    print(f"Error: Private key file not found at {os.path.abspath(PRIVATE_KEY_FILE)}")
    exit()
except Exception as e:
    print(f"Error reading or deserializing private key: {e}")
    exit()


# --- Establish Snowflake Connection ---
try:
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        account=SNOWFLAKE_ACCOUNT,
        private_key=pkb,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )

    print("Successfully connected to Snowflake using key pair authentication!")

    # --- Example Usage ---
    cur = conn.cursor()
    try:
        cur.execute("SELECT current_version()")
        one_row = cur.fetchone()
        print(f"Snowflake version: {one_row[0]}")
    finally:
        cur.close()  # Close the cursor

except snowflake.connector.errors.ProgrammingError as e:
    # Handle authentication errors specifically if needed
    print(f"Snowflake Programming Error: {e}")
    # Example: Check for specific error codes like invalid user/password, etc.
    # if e.errno == 250001:
    #     print("Invalid user or password.")
except Exception as e:
    print(f"Error connecting to Snowflake: {e}")
finally:
    if "conn" in locals() and conn is not None:
        conn.close()  # Ensure the connection is closed
        print("Snowflake connection closed.")
