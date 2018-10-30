import datetime
import os
import psycopg2

from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']

@app.route("/", methods=('GET', 'POST'))
def index():
    # Connect to database
    conn = psycopg2.connect(host='db', database=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'])
    cur = conn.cursor()

    # Get number of all GET requests of each source
    sql_all = """SELECT source, COUNT(*) FROM weblogs GROUP BY source"""
    cur.execute(sql_all)
    all_stats = dict(cur.fetchall())

    # Get number of success GET requests of each source
    sql_success = """SELECT source, COUNT(*) FROM weblogs WHERE status LIKE \'2__\' GROUP BY source;"""
    cur.execute(sql_success)
    success_stats = dict(cur.fetchall())
    
    default_stats = {
        'remote': "No entries yet!",
        'local' : "No entries yet!",
        'total' : "No entries yet!"
    }

    # Determine if there was at least one request
    if not all_stats:
        all_stats = success_stats = rate_stats = default_stats
    else:
        all_stats['total'] = sum(all_stats.values())
        success_stats['total'] = sum(success_stats.values())
        rate_stats = {key: success_stats[key]/all_stats[key] if all_stats[key]!=0 else 0 for key in all_stats.keys() & success_stats}

    return render_template('index.html', rate = rate_stats, success = success_stats, all = all_stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
