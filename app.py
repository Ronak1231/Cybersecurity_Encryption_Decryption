import streamlit as st
from PIL import Image
import numpy as np
import os
import time
import sqlite3
from cryptography.fernet import Fernet

# Database setup
def create_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

# User registration
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# User login
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Function to generate a Fernet key
def generate_key():
    return Fernet.generate_key()

# Function to encrypt text
def encrypt_text(text, key):
    cipher = Fernet(key)
    encrypted_text = cipher.encrypt(text.encode())
    return encrypted_text

# Function to decrypt text
def decrypt_text(encrypted_text, key):
    cipher = Fernet(key)
    decrypted_text = cipher.decrypt(encrypted_text).decode()
    return decrypted_text

# Function to encode text into an image
def encode_image(image, text):
    img_data = np.array(image)
    text_length = len(text)
    
    if text_length > img_data.size:
        raise ValueError("Text is too long to encode in the image.")
    
    # Check if the image is grayscale or RGB
    if img_data.ndim == 2:  # Grayscale image
        for i in range(text_length):
            img_data[i // img_data.shape[1], i % img_data.shape[1]] = text[i]
    elif img_data.ndim == 3:  # RGB image
        for i in range(text_length):
            img_data[i // img_data.shape[1], i % img_data.shape[1], 0] = text[i]  # Modify the red channel
    else:
        raise ValueError("Unsupported image format.")
    
    return Image.fromarray(img_data)

# Function to extract text from an image
def extract_text(image, length):
    img_data = np.array(image)
    extracted_text = []
    
    if img_data.ndim == 2:  # Grayscale image
        for i in range(length):
            extracted_text.append(img_data[i // img_data.shape[1], i % img_data.shape[1]])
    elif img_data.ndim == 3:  # RGB image
        for i in range(length):
            extracted_text.append(img_data[i // img_data.shape[1], i % img_data.shape[1], 0])  # Read from the red channel
    else:
        raise ValueError("Unsupported image format.")
    
    return bytes(extracted_text)

# Function to encrypt an image using XOR
def encrypt_image_xor(image, key):
    key = key % 256  # Ensure key is within byte range
    encrypted_image = np.bitwise_xor(image, key)
    return encrypted_image.astype(np.uint8)  # Ensure the data type is uint8

# Function to decrypt an image using XOR
def decrypt_image_xor(image, key):
    key = key % 256  # Ensure key is within byte range
    decrypted_image = np.bitwise_xor(image, key)
    return decrypted_image.astype(np.uint8)  # Ensure the data type is uint8

# Function to save an image
def save_image(image, filename):
    if not os.path.exists('encrypt'):
        os.makedirs('encrypt')
    img = Image.fromarray(image)
    img.save(os.path.join('encrypt', filename))

# Create database if it doesn't exist
if not os.path.exists('users.db'):
    create_db()

# Streamlit UI
st.title("🛡️🖥️Steganography and Image Encryption App")

# User authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login/Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Register"):
        if register_user(username, password):
            st.success("User  registered successfully!")
        else:
            st.error("Username already exists.")
    
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password.")
else:
    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ("Encrypt Text", "Decrypt Text", "Encrypt Image", "Decrypt Image", "About", "Logout"))

    if page == "Logout":
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        # No need to rerun, the UI will automatically show the login/register UI

    elif page == "Encrypt Text":
        st.subheader("Encrypt Text into Image")

        # Upload image
        uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

        # Input text to hide
        text_to_hide = st.text_area("Text to hide")

        # Password for encryption
        password = st.text_input("Encryption Password", type='password')

        if st.button("Encrypt"):
            if uploaded_image and text_to_hide and password:
                image = Image.open(uploaded_image)
                key = generate_key()  # Generate a key for this session
                encrypted_text = encrypt_text(text_to_hide, key)
                try:
                    stego_image = encode_image(image, encrypted_text)
                    # Save the encoded image
                    encoded_image_path = 'encrypted_files/encoded_image.png'
                    stego_image.save(encoded_image_path)

                    st.image(stego_image, caption="Encoded Image")
                    st.success("Text has been hidden in the image!")
                    st.write(f"Encoded image saved at: {encoded_image_path}")

                    # Store encrypted text, key, and password in session state
                    st.session_state.encrypted_text = encrypted_text
                    st.session_state.key = key
                    st.session_state.password = password  # Store password
                    
                except ValueError as e:
                    st.error(str(e))

    elif page == "Decrypt Text":
        st.subheader("Decrypt Text from Image")

        # Upload image for decryption
        uploaded_image = st.file_uploader("Upload an Image for Decryption", type=["png", "jpg", "jpeg"])

        # Password for decryption
        password = st.text_input("Decryption Password", type='password')

        if st.button("Decrypt"):
            if uploaded_image and 'encrypted_text' in st.session_state and 'key' in st.session_state and 'password' in st.session_state:
                if password == st.session_state.password:  # Check if passwords match
                    image = Image.open(uploaded_image)
                    length = len(st.session_state.encrypted_text)
                    extracted_text = extract_text(image, length)
                    try:
                        decrypted_text = decrypt_text(extracted_text, st.session_state.key)
                        st.text_area("Decrypted Text", value=decrypted_text, height=200)
                    except Exception as e:
                        st.error("Decryption failed: " + str(e))
                else:
                    st.error("Incorrect decryption password!")
            else:
                st.error("Please upload an image and ensure you have encrypted text available.")
    
    elif page == "Encrypt Image":
        st.subheader("Encrypt Image Using XOR")
        
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        key = st.number_input("Enter a key (0-255):", min_value=0, max_value=255)

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)

            st.image(image, caption='Original Image', use_container_width=True)

            if st.button("Encrypt"):
                encrypted_image = encrypt_image_xor(image_array, key)
                st.image(encrypted_image, caption='Encrypted Image', use_container_width=True)

                # Save the encrypted image with a unique filename
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # Get current timestamp
                filename = f"encrypted_image_{timestamp}.png"
                save_image(encrypted_image, filename)
                st.success(f"Encrypted image saved as 'encrypt/{filename}'")

    elif page == "Decrypt Image":
        st.subheader("Decrypt Image Using XOR")
        
        uploaded_file = st.file_uploader("Choose an encrypted image...", type=["png"])
        key = st.number_input("Enter the key used for encryption (0-255):", min_value=0, max_value=255)

        if uploaded_file is not None:
            encrypted_image = Image.open(uploaded_file)
            encrypted_image_array = np.array(encrypted_image)

            st.image(encrypted_image, caption='Encrypted Image', use_container_width=True)

            if st.button("Decrypt"):
                decrypted_image = decrypt_image_xor(encrypted_image_array, key)
                st.image(decrypted_image, caption='Decrypted Image', use_container_width=True)

                # Save the decrypted image with a unique filename
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # Get current timestamp
                filename = f"decrypted_image_{timestamp}.png"
                save_image(decrypted_image, filename)
                st.success(f"Decrypted image saved as 'encrypt/{filename}'")

    elif page == "About":
        st.subheader("About This App 🛡️🖥️")

        st.markdown("""
        Welcome to the **Steganography and Image Encryption App**! This is a powerful tool that allows you to hide text within images and encrypt images using XOR encryption. It provides an intuitive interface for both beginners and advanced users to use modern encryption techniques effectively.

        ### 🔐 Features:
        - **Encrypt Text into Image**: Hide text inside an image (Steganography) such that it remains invisible to the human eye.
        - **Decrypt Text from Image**: Retrieve the hidden text from an image that was encrypted.
        - **Encrypt Image with XOR**: Securely encrypt an image with a simple XOR encryption technique using a key.
        - **Decrypt Image with XOR**: Decrypt the encrypted image by providing the correct key.

        ### 🌟 Why You Should Use This App?
        - **Privacy**: Protect your sensitive messages by hiding them inside images.
        - **Security**: Encrypt images to keep them safe from unauthorized access.
        - **User-Friendly**: Simple interface that makes encryption and decryption accessible to everyone.
        - **Visual Steganography**: A cool way to hide information in plain sight without raising suspicion.

        ### 📜 How to Use the App:
        
        1. **Encrypt Text into Image**:
            - Upload any image (PNG, JPG, JPEG).
            - Enter the text you want to hide inside the image.
            - Provide a password for encryption.
            - The app will generate an image with the hidden message, which can only be decrypted using the correct password.

        2. **Decrypt Text from Image**:
            - Upload the encoded image with hidden text.
            - Enter the password used for encryption.
            - The app will extract and decrypt the hidden message, allowing you to view it.

        3. **Encrypt Image with XOR**:
            - Upload an image you want to encrypt.
            - Choose a key (between 0 and 255) to encrypt the image.
            - The encrypted image will be generated, which can only be decrypted using the same key.

        4. **Decrypt Image with XOR**:
            - Upload the encrypted image.
            - Enter the key used for encryption.
            - The app will decrypt the image and display the original image.

        ### 📱 Stay Connected:
        - **[GitHub](https://github.com/Ronak1231)**: Explore my other projects and open-source contributions.
        - **[LinkedIn](https://www.linkedin.com/in/ronak-bansal-715605253/)**: Connect with me for professional opportunities and collaborations.
        - **[Email](mailto:ronakbansal12345@gmail.com)**: Get in touch for any questions, feedback, or collaborations.

        ### 🤖 Enjoy Using the App!
        Encrypt your messages, protect your content, and have fun exploring the world of Steganography and Image Encryption! If you encounter any issues or need further assistance, feel free to reach out to me through the contact links above.
        """)
