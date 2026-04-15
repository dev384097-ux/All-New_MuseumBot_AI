# 🏛️ Museum AI Chatbot (Heritage Guide)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-flask-orange.svg)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-green.svg)](https://aistudio.google.com/)
[![Razorpay](https://img.shields.io/badge/Payments-Razorpay%20UPI-blue.svg)](https://razorpay.com/)

A production-grade, multilingual AI chatbot designed for Indian museums. This Capstone project integrates cutting-edge Generative AI with a robust rule-based fallback system to handle ticket bookings, historical guidance, and museum logistics in multiple Indian languages.

---

## 🌟 Major Highlights

### 🛡️ Verified UPI QR Payments
*   **Professional Integration**: Uses **Razorpay Payment Links** to generate official, verified QR codes that bypass "Security Blocks" in GPay, PhonePe, and Paytm.
*   **Dynamic Scanning**: QR codes are generated on-the-fly with the exact booking amount pre-filled.

### 🔄 Automated Real-Time Verification
*   **Hands-Free Confirmation**: Implements a backend-frontend polling architecture that detects the payment status from Razorpay APIs automatically.
*   **Instant Tickets**: The E-Ticket appears immediately once the payment is successful on the visitor's mobile.

### 🎫 Student Concession & Multi-Tier Pricing
*   **Smart AI Booking**: Chatbot intelligently asks for visitor categories (Adult/Student).
*   **₹1 Fee**: Automatic ₹1 student concession pricing applied during booking.
*   **Premium E-Tickets**: High-contrast, downloadable digital tickets with unique verification hashes.

### 🌐 Polyglot & Script-Pure
*   **10-Language Support**: English, Hindi, Tamil, Punjabi, Bengali, Telugu, Kannada, Malayalam, Gujarati, and Marathi.
*   **Script Consistency**: Automatically detects and responds in both **Native script** (e.g., नमस्ते) and **Romanized/Latin script** (e.g., Namaste).

---

## 📁 Project Architecture

| File / Directory | Role |
| :--- | :--- |
| `app.py` | Main Flask entry point; handles Auth, Payment APIs, and QR generation. |
| `chatbot_engine.py` | AI orchestration, Multilingual state machine, and Tier-based pricing logic. |
| `database.py` | Schema definitions and SQLite connection pooling for bookings. |
| `templates/` | Ginja2 templates for the main interface, Login/OTP, and Chat UI. |
| `static/` | Premium CSS (Glassmorphism), Vanilla JS (Payment Polling), and Design Assets. |

---

## 🚀 Getting Started

### 1. Configure Environment
Create a `.env` file from the example:
```bash
GEMINI_API_KEY=your_key
RAZORPAY_KEY_ID=your_razorpay_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
BUSINESS_UPI_ID=your_vpa@okaxis
```

### 2. Manual Installation
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

---

## 🔑 Key Environment Variables

| Variable | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google AI Studio key. |
| `RAZORPAY_KEY_ID` | Razorpay Key ID for payments. |
| `RAZORPAY_KEY_SECRET` | Razorpay Secret Key. |
| `BUSINESS_UPI_ID` | The UPI ID where payments will be settled. |
| `MAIL_USERNAME` | SMTP Email (Gmail). |
| `MAIL_PASSWORD` | Gmail App Password. |

---

*Created as part of the Museum AI Capstone Project for SIH 1648.*
