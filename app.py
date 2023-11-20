from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re  # Import the regular expression module

app = Flask(__name__)

# Function to get a new SQLite connection
def get_db():
    return sqlite3.connect('videos.db')

# Create a SQLite table
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT NOT NULL,
            counter INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['video_link']

        # Insert video into the database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO videos (link) VALUES (?)', (link,))
            conn.commit()

    # Fetch video data from the database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, link, counter FROM videos')
        videos = cursor.fetchall()

    return render_template('index.html', videos=videos)

@app.route('/watch_video/<int:video_id>', methods=['GET'])
def watch_video(video_id):
    # Fetch the video link from the database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT link FROM videos WHERE id = ?', (video_id,))
        video_link = cursor.fetchone()[0]

    # Extract the Dailymotion video ID from the link using a regular expression
    video_id_match = re.match(r'https?://www\.dailymotion\.com/video/([a-zA-Z0-9]+)', video_link)
    
    if video_id_match:
        dailymotion_video_id = video_id_match.group(1)
        embed_url = f"https://www.dailymotion.com/embed/video/{dailymotion_video_id}"

        return render_template('watch_video.html', embed_url=embed_url, video_id=video_id)
    else:
        # Handle invalid Dailymotion link
        return "Invalid Dailymotion link"


@app.route('/increase_counter/<int:video_id>', methods=['POST'])
def increase_counter(video_id):
    # Increment the counter for the video
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE videos SET counter = counter + 1 WHERE id = ?', (video_id,))
        conn.commit()

    return redirect(url_for('index'))

# Add this route to handle video deletion
@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    # Delete the video from the database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        conn.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
