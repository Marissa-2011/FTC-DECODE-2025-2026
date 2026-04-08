from flask import Flask, render_template_string, request, redirect, url_for, session
import csv
import os

'''INFORMATION: to edit the table go to analysis page and add more categories,
also go to get pit info
also go to data view this is where everything is handled
we just need to add new categories'''

app = Flask(__name__)
app.secret_key = "ftc_championship_key"

# File setup
user_file = 'users.csv'
pit_file = 'pit_data.csv'
match_file = 'match_data.csv'

# Initialize files
for f_path, headers in [
  (user_file, ['username', 'password']),
  (pit_file, ['scout', 'team_num', 'drive_type', 'notes']),
  (match_file, ['scout', 'team_num', 'match_num', 'points'])
]:
  if not os.path.exists(f_path):
    with open(f_path, 'w', newline='') as f:
      csv.writer(f).writerow(headers)

# --- Design ---
base_style = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body { font-family: sans-serif; margin: 0; background: #f4f7f9; color: #333; }
  nav { background: #2c3e50; padding: 15px; display: flex; gap: 15px; justify-content: center; }
  nav a { color: white; text-decoration: none; font-weight: bold; }
  .container { padding: 20px; max-width: 800px; margin: auto; }
  .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
  input, select, button { width: 100%; padding: 10px; margin: 5px 0 15px 0; border: 1px solid #ccc; border-radius: 4px; }
  button { background: #27ae60; color: white; border: none; cursor: pointer; font-size: 16px; }
  button:hover { background: #219150; }
  table { width: 100%; border-collapse: collapse; background: white; }
  th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
  th { background: #ecf0f1; }
</style>
'''

nav_bar = '''
<nav>
  <a href="/">Home</a>
  <a href="/pit">Pit Scout</a>
  <a href="/match">Match Scout</a>
  <a href="/data">Analysis</a>
  <a href="/logout">Logout</a>
</nav>
'''

# --- Pages ---

home_page = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h1>Welcome to FTC Scouting</h1>
    <p>Logged in as: <strong>{{ user }}</strong></p>
    <hr>
    <h3>How it Works</h3>
    <ul>
      <li><strong>Pit Scouting:</strong> meep </li>
      <li><strong>Match Scouting:</strong> beep</li>
      <li><strong>Analysis:</strong> boop</li>
      <li><strong>Average Points</strong> meep.</li>
    </ul>
  </div>
</div>
'''

pit_form = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>New Pit Report</h2>
    <form method="POST">
      <input type="number" name="team_num" placeholder="Team Number" required>
      <label>Drivetrain Type:</label>
      <select name="drive_type">
        <option value="Mecanum">Mecanum</option>
        <option value="Tank">Tank</option>
        <option value="Swerve">Swerve</option>
      </select>
      <input type="text" name="notes" placeholder="General Robot Description">
      <button type="submit">Save Pit Data</button>
    </form>
  </div>
</div>
'''

match_form = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>New Match Report</h2>
    <form method="POST">
      <input type="number" name="team_num" placeholder="Team Number" required>
      <input type="number" name="match_num" placeholder="Match Number" required>
      <input type="number" name="points" placeholder="Total Points Scored" required>
      <button type="submit">Save Match Data</button>
    </form>
  </div>
</div>
'''

#THIS IS THE TABLE AND HOW TO ADD NEW COLUMNS
analysis_page = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>Team Rankings & Analysis</h2>
    <form method="GET" action="/data">
      <input type="number" name="filter_team" placeholder="Filter by Team Number...">
      <button type="submit" style="background:#3498db">Apply Filter</button>
      <a href="/data" style="font-size: 12px;">Clear Filter</a>
    </form>
    <br>
    <table>
      <tr>
        <th>Team #</th>
        <th>Avg Points</th>
        <th>Total Matches</th>
        <th>Drive Type</th>
        <th>Notes</th>
      </tr>
      {% for team, stats in results.items() %}
      <tr>
        <td>{{ team }}</td>
        <td>{{ stats.avg }}</td>
        <td>{{ stats.count }}</td>
        <td>{{ stats.drive }}</td>
        <td>{{ stats.notes }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>
</div>
'''


# --- Logic ---

def get_pit_info():
  info = {}
  with open(pit_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      info[row['team_num']] = {
      'drive_type':row['drive_type'],
      'notes':row['notes']
      }

  return info

def get_match_info():
  info = {}
  with open(match_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      info[row['team_num']] = {
      'match_num':row['match_num'],
      'points':row['points']}
  return info


@app.route('/')
def home():
  if 'user' not in session: return redirect('/login')
  return render_template_string(home_page, user=session['user'])


@app.route('/pit', methods=['GET', 'POST'])
def pit():
  if 'user' not in session: return redirect('/login')
  if request.method == 'POST':
    with open(pit_file, 'a', newline='') as f:
      csv.writer(f).writerow(
        [session['user'], request.form['team_num'], request.form['drive_type'], request.form['notes']])
    return redirect('/')
  return render_template_string(pit_form)


@app.route('/match', methods=['GET', 'POST'])
def match():
  if 'user' not in session: return redirect('/login')
  if request.method == 'POST':
    with open(match_file, 'a', newline='') as f:
      csv.writer(f).writerow(
        [session['user'], request.form['team_num'], request.form['match_num'], request.form['points']])
    return redirect('/')
  return render_template_string(match_form)


@app.route('/data') # displaying table
def data_view():
  if 'user' not in session: return redirect('/login')

  filter_team = request.args.get('filter_team')
  pit_dict = get_pit_info()
  team_stats = {}

  for t, info in pit_dict.items():
    if filter_team and t != filter_team: continue
    team_stats[t] = {
      'total': 0,
      'count': 0,
      'avg':0.0,
      'drive': info['drive_type'],
      'notes': info['notes']
    }

  # 2. NOW open the match file
  with open(match_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      t = row['team_num']

      # If they are already on the whiteboard (from the Pit info), we just update
      if t in team_stats:
        team_stats[t]['total'] += int(row['points'])
        team_stats[t]['count'] += 1
        team_stats[t]['avg'] = round(team_stats[t]['total'] / team_stats[t]['count'], 1)
      else:
        # If they AREN'T on the board (Match only), add them now as 'Unknown'
        team_stats[t] = {
          'total': int(row['points']),
          'count': 1,
          'avg': int(row['points']),
          'drive': 'Unknown',
          'notes': 'N/A'
        }
  return render_template_string(analysis_page, results=team_stats)


#OLD DATA_VIEW
'''
def data_view():
  if 'user' not in session: return redirect('/login')

  filter_team = request.args.get('filter_team')
  pit_dict = get_pit_info()
  team_stats = {}

  with open(match_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      t = row['team_num']
      if filter_team and t != filter_team: continue

      p = int(row['points'])
      if t not in team_stats:
        pitinf = pit_dict.get(t, {'drive_type':'Unknown', 'notes':'No Notes'})
        team_stats[t] = {'total': 0, 'count': 0, 'drive':pitinf['drive_type'], 'notes':pitinf['notes']}

      team_stats[t]['total'] += p
      team_stats[t]['count'] += 1
      team_stats[t]['avg'] = round(team_stats[t]['total'] / team_stats[t]['count'], 1)

  return render_template_string(analysis_page, results=team_stats)
'''


# (Login/Register/Logout logic stays same as previous)
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    u, p = request.form['username'], request.form['password']
    with open(user_file, 'r') as f:
      for row in csv.reader(f):
        if row and row[0] == u and row[1] == p:
          session['user'] = u
          return redirect('/')
    return "Invalid login"
  return render_template_string(
    base_style + '<div class="container"><div class="card"><h2>Login</h2><form method="POST"><input name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><button>Login</button></form><a href="/register">Register</a></div></div>')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    with open(user_file, 'a', newline='') as f:
      csv.writer(f).writerow([request.form['username'], request.form['password']])
    return redirect('/login')
  return render_template_string(
    base_style + '<div class="container"><div class="card"><h2>Register</h2><form method="POST"><input name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><button>Create Account</button></form></div></div>')


@app.route('/logout')
def logout():
  session.clear()
  return redirect('/login')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)