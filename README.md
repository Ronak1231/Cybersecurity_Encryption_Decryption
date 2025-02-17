# 🛡️ Steganography & Image Encryption App

A secure and easy-to-use **Steganography and Image Encryption App** built with **Streamlit, Python, and SQLite**. 
This app enables users to **hide text in images, encrypt/decrypt images using XOR**, and manage **user authentication securely**.

## 🚀 Features

✅ **User Authentication**: Secure login & registration system with SQLite.  
✅ **Text Steganography**: Hide and extract encrypted text inside images.  
✅ **Image Encryption**: Encrypt and decrypt images using XOR bitwise operations.  
✅ **Key-based Encryption**: Uses `cryptography.fernet` for text encryption.  
✅ **Streamlit UI**: Interactive web-based interface for easy usability.  

## 🏗️ Installation

1️⃣ Clone this repository:
```bash
git clone https://github.com/yourusername/steganography-encryption-app.git
cd steganography-encryption-app
```

2️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```

3️⃣ Run the application:
```bash
streamlit run app.py
```

## 📂 Project Structure

```
steganography-encryption-app/
│── encrypt/                   # Directory to store encrypted images for Text
│── encrypted_files/           # Directory to store encrypted images for Image Encryption
│── users.db                    # SQLite database for user authentication
│── app.py                      # Main Streamlit app
│── requirements.txt             # Python dependencies
│── README.md                    # Project documentation
│── LICENSE                      # Project license
└── images/                      # Sample images (if needed)
```

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## 🤝 Contributing

1. Fork the repo and create a new branch.
2. Commit your changes and push them.
3. Create a Pull Request.

## ✨ Credits

- Developed using **Python**, **Streamlit**, **NumPy**, **SQLite**, and **PIL**.
- Inspired by modern cryptographic techniques.

## ✍️ Author

Developed by [Ronak Bansal](https://github.com/Ronak1231)  
🔗 LinkedIn: [Ronak Bansal](https://www.linkedin.com/in/ronak-bansal-715605253/)  
📧 Email: ronakbansal12345@gmail.com

---

💙 **Happy Encrypting!**
