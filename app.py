from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pymysql
app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
db = mysql.connector.connect(
    host="database-1.cdyosa6weglp.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="ArthForm123",
    database="mail_system"
)

# Home Route (Login Page)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('inbox'))
    return render_template('login.html')

# Inbox Route
@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    cursor = db.cursor(dictionary=True)

    # Fetch emails and join with users table to get sender names
    cursor.execute("""
        SELECT emails.*, users.username as sender_name
        FROM emails
        JOIN users ON emails.sender_id = users.id
        WHERE recipient_id = %s
        ORDER BY timestamp DESC
    """, (user_id,))
    emails = cursor.fetchall()

    cursor.close()
    return render_template('inbox.html', emails=emails)


# Email View Route
@app.route('/view_email/<int:email_id>')
def view_email(email_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = db.cursor(dictionary=True)

    # Update read_status to 1 (read)
    cursor.execute("UPDATE emails SET read_status = 1 WHERE id = %s", (email_id,))
    db.commit()

    # Fetch the email content along with the sender's name
    cursor.execute("""
        SELECT emails.*, users.username as sender_name
        FROM emails
        JOIN users ON emails.sender_id = users.id
        WHERE emails.id = %s
    """, (email_id,))
    email = cursor.fetchone()

    cursor.close()
    return render_template('view_email.html', email=email)



# Drafts Route
@app.route('/drafts')
def drafts():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM drafts WHERE user_id=%s", (session['user_id'],))
    drafts = cursor.fetchall()
    cursor.close()
    return render_template('drafts.html', drafts=drafts)

# Save Draft Route
@app.route('/save_draft', methods=['POST'])
def save_draft():
    subject = request.form['subject']
    content = request.form['content']
    cursor = db.cursor()
    cursor.execute("INSERT INTO drafts (user_id, subject, content) VALUES (%s, %s, %s)",
                   (session['user_id'], subject, content))
    db.commit()
    cursor.close()
    return redirect(url_for('drafts'))

# Reply Route
@app.route('/reply/<int:email_id>', methods=['GET', 'POST'])
def reply(email_id):
    if request.method == 'POST':
        reply_content = request.form['content']
        cursor = db.cursor()
        cursor.execute("INSERT INTO emails (sender_id, recipient_id, subject, content, read_status) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], email_id, "RE: Your Subject", reply_content, False))
        db.commit()
        cursor.close()
        return redirect(url_for('inbox'))

    cursor = db.cursor()
    cursor.execute("SELECT * FROM emails WHERE id=%s", (email_id,))
    email = cursor.fetchone()
    cursor.close()
    return render_template('reply.html', email=email)
# Report Spam Route
@app.route('/report_spam/<int:email_id>', methods=['POST'])
def report_spam(email_id):
    user_id = session.get('user_id')
    cursor = db.cursor()

    # Insert into spam_reports table (make sure you have created this table)
    cursor.execute("INSERT INTO spam_reports (user_id, email_id) VALUES (%s, %s)", (user_id, email_id))
    db.commit()
    cursor.close()

    return 'Thanks for reporting! Your feedback helps us improve.', 200  # Return a success message

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
