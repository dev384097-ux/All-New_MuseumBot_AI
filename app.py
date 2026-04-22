from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import random
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot_engine import MuseumChatbot
from database import init_db, get_db_connection
import razorpay
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import qrcode
import io
import base64
import time

# --- UNIFIED EMAIL SERVICE ---
def send_otp_email(email, name, otp):
    """
    Consolidated email sender with multi-provider failover.
    Priority: 1. Brevo (New) -> 2. SendGrid -> 3. SMTP (Gmail)
    """
    subject = "Your MuseumBot Verification Code"
    body = f"Hello {name},\n\nYour One-Time Password (OTP) for MuseumBot is: {otp}\n\nPlease enter this on the verification page to complete your login."
    
    # 1. BREVO (Primary)
    brevo_key = os.getenv('BREVO_API_KEY', '').strip()
    if brevo_key:
        print("DEBUG: Attempting Brevo API delivery...")
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = brevo_key
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            
            sender_email = os.getenv('SENDER_EMAIL', 'botonlinemuseum@gmail.com').strip()
            html_body = f"<html><body><p>{body.replace(chr(10), '<br>')}</p></body></html>"
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                sender={"name": "MuseumBot AI", "email": sender_email},
                to=[{"email": email, "name": name}],
                subject=subject,
                text_content=body,
                html_content=html_body
            )
            api_instance.send_transac_email(send_smtp_email)
            print("DEBUG: Email sent via Brevo successfully!")
            return True
        except ApiException as e:
            print(f"DEBUG: Brevo API failed: {str(e)}")
            
    # 2. SENDGRID (Secondary)
    sendgrid_key = os.getenv('SENDGRID_API_KEY', '').strip()
    if sendgrid_key:
        print("DEBUG: Using SendGrid API fallback...")
        try:
            sg_client = SendGridAPIClient(sendgrid_key)
            sender = os.getenv('SENDER_EMAIL', 'botonlinemuseum@gmail.com').strip()
            message = SendGridMail(
                from_email=sender,
                to_emails=email,
                subject=subject,
                plain_text_content=body
            )
            sg_client.send(message)
            print("DEBUG: Email sent via SendGrid successfully!")
            return True
        except Exception as sg_err:
            print(f"DEBUG: SendGrid API failed: {str(sg_err)}")

    # 3. SMTP (Final Attempt)
    try:
        import socket
        socket.setdefaulttimeout(5)
        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)
        print("DEBUG: Email sent via SMTP successfully!")
        return True
    except Exception as e:
        print(f"CRITICAL SMTP ERROR: {str(e)}")
        return False

from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Enable ProxyFix to handle HTTPS redirects correctly behind Render's proxy
# Enhanced ProxyFix for Render
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
app.secret_key = os.getenv('SECRET_KEY', 'development_only_key_please_set_in_env')

# Detect if we are on Render for protocol enforcement
IS_RENDER = 'RENDER' in os.environ

if IS_RENDER:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
else:
    # Allow OAuth over HTTP for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', '').strip(),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', '').strip(),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# SMTP Configuration (Port 587 is standard for Render/Heroku)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# Aggressively sanitize password (remove all spaces as Gmail app passwords are internally spaceless)
password = os.getenv('MAIL_PASSWORD', '').replace(' ', '').strip()
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '').strip()
app.config['MAIL_PASSWORD'] = password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', '').strip()
app.config['MAIL_DEBUG'] = True

mail = Mail(app)

if not os.path.exists(os.path.join(os.path.dirname(__file__), 'data', 'museum.db')):
    with app.app_context():
        init_db()

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'secret_placeholder')
rzp_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

chatbot = MuseumChatbot()

@app.route('/debug-url')
def debug_url():
    # This route helps diagnose redirect_uri_mismatch errors
    scheme = 'https' if IS_RENDER else 'http'
    uri = url_for('google_callback', _external=True, _scheme=scheme).strip()
    return f"""
    <h3>Google OAuth Diagnostic</h3>
    <p><strong>Actual Redirect URI being sent:</strong> <code style='background:#eee;padding:5px;'>{uri}</code></p>
    <p>Copy the code above and paste it into your <a href='https://console.cloud.google.com/apis/credentials' target='_blank'>Google Cloud Console</a> under 'Authorized redirect URIs'.</p>
    <p><strong>Environment:</strong> {'Production (Render)' if IS_RENDER else 'Local'}</p>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
            
        conn.execute('INSERT INTO users (username, email, password_hash, is_verified) VALUES (?, ?, ?, 1)',
                     (username, username, generate_password_hash(password)))
        conn.commit()
        conn.close()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['full_name'] or user['username']
            return redirect(url_for('home'))
            
        flash('Invalid username or password.')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    is_logged_in = 'user_id' in session
    username = session.get('username', None)
    
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
    # Fetch latest announcements
    conn = get_db_connection()
    announcements = conn.execute('SELECT * FROM announcements WHERE is_active = 1 ORDER BY id DESC').fetchall()
    museums_rows = conn.execute('SELECT * FROM exhibitions').fetchall()
    museums = [dict(row) for row in museums_rows]
    conn.close()
    
    return render_template('index.html', 
                          logged_in=is_logged_in, 
                          username=username,
                          rzp_key_id=RAZORPAY_KEY_ID,
                          announcements=announcements,
                          museums=museums)



@app.route('/login/google')
def login_google():
    if not os.getenv('GOOGLE_CLIENT_ID') or "your" in os.getenv('GOOGLE_CLIENT_ID').lower():
        # Mock Google Login for development
        mock_user = {
            'email': 'visitor@example.com',
            'name': 'Heritage Visitor'
        }
        return google_mock_callback(mock_user)
        
    # Explicitly force HTTPS for the redirect URI on Render to avoid protocol mismatch
    redirect_uri = url_for('google_callback', _external=True)
    if IS_RENDER and redirect_uri.startswith('http://'):
        redirect_uri = redirect_uri.replace('http://', 'https://')
        
    return google.authorize_redirect(redirect_uri)

def google_mock_callback(user_info):
    email = user_info['email']
    name = user_info['name']
    
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        conn.execute('UPDATE users SET otp = ?, full_name = ? WHERE email = ?', (otp, name, email))
    else:
        conn.execute('INSERT INTO users (username, email, full_name, otp, is_verified) VALUES (?, ?, ?, ?, 0)',
                     (email, email, name, otp))
    
    conn.commit()
    conn.close()
    
    # Send OTP using unified service
    success = send_otp_email(email, name, otp)
    if not success:
        print(f"MOCK FAILSAFE: OTP for {email} is {otp}")
        session['mock_otp'] = otp
        flash(f"Check server console for OTP (Delivery failed).")
            
    session['temp_email'] = email
    session['temp_name'] = name
    return redirect(url_for('verify_otp'))

@app.route('/auth/callback')
def google_callback():
    try:
        # 1. Authorize Token (Protocol handled automatically by ProxyFix/IS_RENDER)
        print("DEBUG: Initiating Google authorize_access_token...")
        token = google.authorize_access_token()
        
        user_info = token.get('userinfo')
        if not user_info:
            user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
            
        if not user_info:
            print("ERROR: Failed to retrieve user info from Google")
            flash("Failed to retrieve user information from Google.")
            return redirect(url_for('login'))
            
        email = user_info['email'].strip()
        name = user_info.get('name', email.split('@')[0])
        print(f"DEBUG: Successfully fetched user: {email}")
        
        # 2. Database Sync
        otp = str(random.randint(100000, 999999))
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            conn.execute('UPDATE users SET otp = ?, full_name = ? WHERE email = ?', (otp, name, email))
        else:
            conn.execute('INSERT INTO users (username, email, full_name, otp, is_verified) VALUES (?, ?, ?, ?, 0)',
                         (email, email, name, otp))
        
        conn.commit()
        conn.close()
        
        # 3. Send OTP using unified service (Brevo -> SendGrid -> SMTP)
        success = send_otp_email(email, name, otp)
        
        if success:
            session['temp_email'] = email
            session['temp_name'] = name
            return redirect(url_for('verify_otp'))
        else:
            print(f"[FAIL-SAFE] OTP for {email} is: {otp}")
            flash(f"Email service temporarily unreachable. Code has been logged to the server console.", "warning")
            session['temp_email'] = email
            session['temp_name'] = name
            return redirect(url_for('verify_otp'))
            
    except Exception as e:
        print(f"CRITICAL OAUTH CALLBACK ERROR: {str(e)}")
        flash(f"Google Login failed: {str(e)}", "danger")
        return redirect(url_for('login'))

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('temp_email')
    name = session.get('temp_name')
    if not email:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user and user['otp'] == otp_input:
            conn.execute('UPDATE users SET is_verified = 1, otp = NULL WHERE email = ?', (email,))
            conn.commit()
            
            session['user_id'] = user['id']
            session['username'] = user['full_name'] or user['username']
            session.pop('temp_email', None)
            session.pop('temp_name', None)
            conn.close()
            return redirect(url_for('home'))
        else:
            conn.close()
            flash("Invalid OTP. Please try again.")
            
    return render_template('verify_otp.html', email=email, name=name)

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'response': 'Please log in first.'}), 401
        
    user_message = request.json.get('message', '')
    bot_state = session.get('chatbot_state', {'state': 'idle'})
    
    # Ensure backend passes the real logged-in name to the bot for ticketing
    if 'username' in session:
        bot_state['visitor_name'] = session['username']
    
    try:
        response_text, updated_state = chatbot.process_message(user_message, bot_state)
        session['chatbot_state'] = updated_state
        session.modified = True
        return jsonify({'response': response_text})
    except Exception as e:
        print(f"ERROR in /api/chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'response': "I am sorry, but I encountered an internal error. Please try again later."}), 500

@app.route('/api/pay', methods=['POST'])
def pay():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
        
    bot_state = session.get('chatbot_state', {'state': 'idle'})
    user_id = session['user_id']
    
    # Delegate to chatbot to handle the state transition and save booking
    res, updated_state = chatbot.process_payment_success(bot_state, user_id)
    
    session['chatbot_state'] = updated_state
    session.modified = True
    
    return jsonify(res)

@app.route('/api/create_razorpay_order', methods=['POST'])
def create_razorpay_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    amount = int(float(data.get('amount', 0)) * 100) # Convert to paise
    
    try:
        order_params = {
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        }
        order = rzp_client.order.create(data=order_params)
        return jsonify({'success': True, 'order_id': order['id']})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/verify_razorpay_payment', methods=['POST'])
def verify_razorpay_payment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    
    # Booking details for DB
    museum_title = data.get('museum')
    visitor_name = data.get('visitor_name')
    visit_date = data.get('visit_date', 'Not Selected')
    count = int(data.get('count', 1))
    total = float(data.get('total', 0))
    user_id = session['user_id']

    try:
        # Verify Payment Signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        rzp_client.utility.verify_payment_signature(params_dict)
        
        # Payment is verified SUCCESSFUL
        conn = get_db_connection()
        exhib = conn.execute('SELECT id FROM exhibitions WHERE title = ?', (museum_title,)).fetchone()
        ex_id = exhib['id'] if exhib else 99
        
        ticket_hash = str(uuid.uuid4())[:8].upper()
        
        conn.execute(
            'INSERT INTO bookings (user_id, visitor_name, visit_date, exhibition_id, num_tickets, total_price, ticket_hash, status, razorpay_order_id, razorpay_payment_id, razorpay_signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, visitor_name, visit_date, ex_id, count, total, ticket_hash, 'Confirmed', razorpay_order_id, razorpay_payment_id, razorpay_signature)
        )
        conn.commit()
        conn.close()
        
        # If this was from a chatbot flow, clear the state
        if 'chatbot_state' in session:
            session['chatbot_state'] = {'state': 'idle'}
            session.modified = True

        return jsonify({
            'success': True, 
            'ticket_no': ticket_hash,
            'message': 'Payment Verified & Booking Confirmed!'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Payment Verification Failed: {str(e)}'}), 400

@app.route('/api/manual_book', methods=['POST'])
def manual_book():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in before booking.'}), 401
    
    data = request.json
    user_id = session['user_id']
    museum_title = data.get('museum')
    visitor_name = data.get('visitor_name')
    visit_date = data.get('visit_date', 'Not Selected')
    count = int(data.get('count', 1))
    total = float(data.get('total', 0))
    
    conn = get_db_connection()
    # Try to find the correct exhibition_id based on the museum title
    exhib = conn.execute('SELECT id FROM exhibitions WHERE title = ?', (museum_title,)).fetchone()
    ex_id = exhib['id'] if exhib else 99 # Fallback to 99 if not found
    
    ticket_hash = str(uuid.uuid4())[:8].upper()
    
    conn.execute(
        'INSERT INTO bookings (user_id, visitor_name, visit_date, exhibition_id, num_tickets, total_price, ticket_hash) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, visitor_name, visit_date, ex_id, count, total, ticket_hash)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'ticket_no': ticket_hash,
        'message': f'Booking for {museum_title} successful!'
    })

@app.route('/api/generate_upi_qr', methods=['POST'])
def generate_upi_qr():
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        museum_title = data.get('museum', 'Museum Visit')
        visitor_name = data.get('visitor_name', 'Guest')
        
        # Razorpay expects amount in paise (1 INR = 100 Paise)
        paise_amount = int(amount * 100)
        
        # Create a professional Razorpay Payment Link
        # This link generates a verified QR code and bypasses banking security blocks
        # We set expire_by to 15 mins from now
        expire_time = int(time.time() + 900) 
        
        # Create a simplified Razorpay Payment Link (Amount + Currency + Description)
        # We strip optional fields like 'customer' to ensure 100% success in Test Mode
        pl_data = {
            "amount": paise_amount,
            "currency": "INR",
            "description": f"Ticket for {museum_title}"
        }
        
        payment_link = rzp_client.payment_link.create(data=pl_data)
        upi_url = payment_link['short_url']
        payment_link_id = payment_link['id']
        
        # Now generate a QR code for the URL (Verified Link or Manual UPI)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_str = base64.b64encode(buf.getvalue()).decode()
        
        return jsonify({
            'success': True, 
            'qr_code': f"data:image/png;base64,{img_str}",
            'payment_link_id': payment_link_id
        })
    except Exception as e:
        print(f"QR/Link Generation Error: {str(e)}")
        # Ultimate Fallback for Render issues (e.g. library conflict)
        return jsonify({
            'success': False, 
            'message': f"Production Error: {str(e)}. Please check Render Logs."
        }), 500

@app.route('/api/check_payment_status', methods=['POST'])
def check_payment_status():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
        
    data = request.json
    order_id = data.get('order_id') # For Card flow
    link_id = data.get('payment_link_id') # For UPI/QR flow
    
    # Booking details
    museum_title = data.get('museum')
    visitor_name = data.get('visitor_name')
    visit_date = data.get('visit_date', 'Not Selected')
    count = int(data.get('count', 1))
    total = float(data.get('total', 0))
    user_id = session['user_id']

    try:
        is_paid = False
        status = 'created'
        final_order_id = order_id
        
        # 1. Handle Demo Simulation IDs (Prevent API errors if keys are placeholders or IDs are simulated)
        if (link_id and str(link_id).startswith('DEMO_')) or (order_id and str(order_id).startswith('DEMO_')):
            print(f"DEBUG: Handling Simulated ID (Link: {link_id}, Order: {order_id})")
            # For simulation, we just return 'created' so polling continues, 
            # unless some other logic triggers a success.
            return jsonify({'success': True, 'paid': False, 'status': 'created'})

        if link_id:
            # Check Payment Link Status
            try:
                pl = rzp_client.payment_link.fetch(link_id)
                status = pl['status']
                print(f"DEBUG: Payment Link {link_id} | Status: {status}")
                
                if status == 'paid':
                    is_paid = True
                    final_order_id = pl.get('order_id', order_id)
                elif status in ['cancelled', 'expired']:
                    # Record the failure/expiry in the DB
                    conn = get_db_connection()
                    existing = conn.execute('SELECT id FROM bookings WHERE razorpay_order_id = ?', (final_order_id or link_id,)).fetchone()
                    if not existing:
                        exhib = conn.execute('SELECT id FROM exhibitions WHERE title = ?', (museum_title,)).fetchone()
                        ex_id = exhib['id'] if exhib else 99
                        ticket_hash = "FAIL-" + str(uuid.uuid4())[:4].upper()
                        conn.execute(
                            'INSERT INTO bookings (user_id, visitor_name, visit_date, exhibition_id, num_tickets, total_price, ticket_hash, status, razorpay_order_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (user_id, visitor_name, visit_date, ex_id, count, total, ticket_hash, status.capitalize(), final_order_id or link_id)
                        )
                        conn.commit()
                    conn.close()
                    return jsonify({'success': True, 'paid': False, 'status': status, 'message': f'Payment link {status}'})
                else:
                    # Check if there are any failed payments for this link
                    # We check the order ID associated with the link
                    target_order_id = pl.get('order_id')
                    try:
                        search_params = {'order_id': target_order_id} if target_order_id else {'payment_link_id': link_id}
                        payments = rzp_client.payment.all(search_params)
                        p_items = payments.get('items', [])
                        
                        if p_items:
                            recent = p_items[0]
                            print(f"DEBUG: Recent Payment ID: {recent['id']} | Status: {recent['status']}")
                            if recent['status'] == 'failed':
                                # Record failed attempt
                                conn = get_db_connection()
                                existing = conn.execute('SELECT id FROM bookings WHERE razorpay_order_id = ?', (target_order_id or link_id,)).fetchone()
                                if not existing:
                                    exhib = conn.execute('SELECT id FROM exhibitions WHERE title = ?', (museum_title,)).fetchone()
                                    ex_id = exhib['id'] if exhib else 99
                                    ticket_hash = "FAIL-" + str(uuid.uuid4())[:4].upper()
                                    conn.execute(
                                        'INSERT INTO bookings (user_id, visitor_name, visit_date, exhibition_id, num_tickets, total_price, ticket_hash, status, razorpay_order_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                        (user_id, visitor_name, visit_date, ex_id, count, total, ticket_hash, 'Failed', target_order_id or link_id)
                                    )
                                    conn.commit()
                                conn.close()

                                return jsonify({
                                    'success': True, 
                                    'paid': False, 
                                    'status': 'failed', 
                                    'message': recent.get('error_description', 'Payment Failed')
                                })

                    except Exception as e:
                        print(f"Non-critical: Error fetching payments: {str(e)}")
            except Exception as e:
                print(f"DEBUG: API Error fetching link status: {str(e)}")
                # If we get a 404 or Authentication error, we shouldn't just say 'created'
                if "404" in str(e) or "authentication" in str(e).lower():
                    return jsonify({'success': False, 'message': 'Payment provider error or invalid ID'})

        elif order_id:
            # Check Order Status
            try:
                order = rzp_client.order.fetch(order_id)
                status = order['status']
                if status == 'paid':
                    is_paid = True
                elif status in ['cancelled', 'expired']:
                    return jsonify({'success': True, 'paid': False, 'status': status, 'message': f'Order {status}'})
            except Exception as e:
                print(f"DEBUG: API Error fetching order status: {str(e)}")

        if is_paid:
            # Create booking in DB if not already created
            conn = get_db_connection()
            existing = None
            if final_order_id:
                existing = conn.execute('SELECT id FROM bookings WHERE razorpay_order_id = ?', (final_order_id,)).fetchone()
            
            if not existing:
                exhib = conn.execute('SELECT id FROM exhibitions WHERE title = ?', (museum_title,)).fetchone()
                ex_id = exhib['id'] if exhib else 99
                ticket_hash = str(uuid.uuid4())[:8].upper()
                
                conn.execute(
                    'INSERT INTO bookings (user_id, visitor_name, visit_date, exhibition_id, num_tickets, total_price, ticket_hash, status, razorpay_order_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (user_id, visitor_name, visit_date, ex_id, count, total, ticket_hash, 'Confirmed', final_order_id)
                )
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'paid': True, 'ticket_no': ticket_hash})
            else:
                conn.close()
                return jsonify({'success': True, 'paid': True, 'ticket_no': 'ALREADY_EXISTS'})
                
        return jsonify({'success': True, 'paid': False, 'status': status})
    except Exception as e:
        print(f"Poll Error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        flash('Please log in to view your bookings.')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    username = session.get('username', 'Guest')
    
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.*, e.title as museum_name, e.description as museum_desc
        FROM bookings b
        LEFT JOIN exhibitions e ON b.exhibition_id = e.id
        WHERE b.user_id = ?
        ORDER BY b.id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    
    return render_template('my_bookings.html', 
                           bookings=bookings, 
                           logged_in=True, 
                           username=username)

if __name__ == '__main__':

    app.run(debug=True, port=5000)