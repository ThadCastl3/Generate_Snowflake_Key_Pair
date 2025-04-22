import getpass
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def write_key_pair(username: str, password: bytes, directory: str):
    """Generates an RSA private key and writes it to a PEM file in the specified directory."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password),
    )
    filename = os.path.join(directory, f"{username}_key.pem")
    with open(filename, "wb") as f:
        f.write(private_pem)
    print(f"Private key saved to {filename}")
    return key  # Return the key object for public key generation


def write_public_key(username: str, key, directory: str):
    """Writes the public key corresponding to the private key to a PEM file in the specified directory."""
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    filename = os.path.join(directory, f"{username}_key_pub.pem")
    with open(filename, "wb") as f:
        f.write(public_pem)
    print(f"Public key saved to {filename}")


def main():
    username = input("Enter username for snowflake key pair: ")
    password = getpass.getpass("Enter passphrase for private key: ").encode()
    directory_input = input("Enter directory to save key pair (leave blank for current directory): ")

    # Use current directory if input is blank, otherwise use the provided directory
    save_directory = directory_input if directory_input else "./keys"

    if save_directory != ".":
        os.makedirs(save_directory, exist_ok=True)

    # Generate and write private key
    private_key = write_key_pair(username, password, save_directory)

    # Write the corresponding public key
    write_public_key(username, private_key, save_directory)


if __name__ == "__main__":
    main()
