from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pdb-secret-2024-change-me')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///peopledb.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── MODELS ──────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    place_of_birth = db.Column(db.String(200), nullable=True)
    school = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    occupation = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_a_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    person_b_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    relation_type = db.Column(db.String(50), nullable=False)
    group_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    person_a = db.relationship('Person', foreign_keys=[person_a_id])
    person_b = db.relationship('Person', foreign_keys=[person_b_id])

# ── AUTH ────────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── TEMPLATES ───────────────────────────────────────────────────────────────

TEMPLATES = {}

TEMPLATES['login.html'] = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PeopleDB — Login</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg: #0a0a0b; --surface: #111114; --border: #2a2a35;
      --accent: #c9a84c; --accent2: #e8c97e;
      --text: #e8e6df; --muted: #7a7870;
      --danger: #c0392b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Mono', monospace;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    /* Geometric background */
    body::before {
      content: '';
      position: fixed; inset: 0;
      background:
        linear-gradient(rgba(201,168,76,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(201,168,76,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
    }
    .login-wrap {
      width: 380px;
      padding: 48px;
      background: var(--surface);
      border: 1px solid var(--border);
      position: relative;
    }
    .login-wrap::before {
      content: '';
      position: absolute;
      top: -1px; left: 40px; right: 40px;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--accent), transparent);
    }
    .logo {
      font-family: 'Cormorant Garamond', serif;
      font-size: 32px;
      font-weight: 600;
      letter-spacing: 4px;
      color: var(--accent);
      text-align: center;
      margin-bottom: 4px;
    }
    .logo span { color: var(--muted); font-weight: 300; }
    .tagline {
      text-align: center;
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 40px;
    }
    .form-label {
      display: block;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }
    .form-group { margin-bottom: 20px; }
    input {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 12px 14px;
      font-family: 'DM Mono', monospace;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }
    input:focus { border-color: var(--accent); }
    .btn {
      width: 100%;
      padding: 12px;
      background: var(--accent);
      color: var(--bg);
      border: none;
      font-family: 'DM Mono', monospace;
      font-size: 12px;
      letter-spacing: 3px;
      text-transform: uppercase;
      cursor: pointer;
      margin-top: 8px;
      transition: background 0.2s;
    }
    .btn:hover { background: var(--accent2); }
    .alert {
      padding: 10px 14px;
      margin-bottom: 20px;
      font-size: 11px;
      border-left: 3px solid var(--danger);
      background: rgba(192,57,43,0.08);
      color: #e57373;
    }
    .footer-note {
      text-align: center;
      margin-top: 24px;
      font-size: 10px;
      color: var(--muted);
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="login-wrap">
    <div class="logo">PEOPLE<span>DB</span></div>
    <div class="tagline">Private Directory</div>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <form method="POST">
      <div class="form-group">
        <label class="form-label">Username</label>
        <input type="text" name="username" autocomplete="username" required/>
      </div>
      <div class="form-group">
        <label class="form-label">Password</label>
        <input type="password" name="password" autocomplete="current-password" required/>
      </div>
      <button type="submit" class="btn">Enter</button>
    </form>
    <div class="footer-note">Access restricted · Private use only</div>
  </div>
</body>
</html>
'''

TEMPLATES['base.html'] = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{% block title %}PeopleDB{% endblock %}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg: #0a0a0b;
      --surface: #111114;
      --surface2: #18181d;
      --border: #2a2a35;
      --accent: #c9a84c;
      --accent2: #e8c97e;
      --text: #e8e6df;
      --muted: #7a7870;
      --danger: #c0392b;
      --success: #27ae60;
      --link: #a8c4d4;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Mono', monospace;
      font-size: 13px;
      min-height: 100vh;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { color: var(--accent2); }

    /* NAV */
    nav {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 56px;
      position: sticky; top: 0; z-index: 100;
    }
    .nav-brand {
      font-family: 'Cormorant Garamond', serif;
      font-size: 22px;
      font-weight: 600;
      letter-spacing: 2px;
      color: var(--accent);
    }
    .nav-brand span { color: var(--muted); font-weight: 300; }
    .nav-links { display: flex; gap: 24px; align-items: center; }
    .nav-links a { color: var(--muted); font-size: 12px; letter-spacing: 1px; text-transform: uppercase; transition: color 0.2s; }
    .nav-links a:hover { color: var(--accent); }

    /* SEARCH BAR */
    .nav-search { display: flex; gap: 0; }
    .nav-search input {
      background: var(--bg);
      border: 1px solid var(--border);
      border-right: none;
      color: var(--text);
      padding: 6px 12px;
      font-family: inherit;
      font-size: 12px;
      width: 180px;
      outline: none;
    }
    .nav-search button {
      background: var(--accent);
      border: none;
      color: var(--bg);
      padding: 6px 12px;
      cursor: pointer;
      font-family: inherit;
      font-size: 11px;
      letter-spacing: 1px;
    }

    /* LAYOUT */
    .container { max-width: 1100px; margin: 0 auto; padding: 40px 24px; }
    .page-header {
      margin-bottom: 40px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .page-title {
      font-family: 'Cormorant Garamond', serif;
      font-size: 36px;
      font-weight: 300;
      letter-spacing: 1px;
    }
    .page-title small {
      display: block;
      font-family: 'DM Mono', monospace;
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    /* CARDS */
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 24px;
      margin-bottom: 16px;
    }
    .card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 16px;
    }
    .person-card {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 20px;
      cursor: pointer;
      transition: border-color 0.2s, transform 0.2s;
      position: relative;
      overflow: hidden;
    }
    .person-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0;
      width: 3px; height: 100%;
      background: var(--accent);
      transform: scaleY(0);
      transition: transform 0.2s;
    }
    .person-card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .person-card:hover::before { transform: scaleY(1); }
    .person-card h3 {
      font-family: 'Cormorant Garamond', serif;
      font-size: 20px;
      font-weight: 400;
      margin-bottom: 8px;
    }
    .person-card .meta { color: var(--muted); font-size: 11px; line-height: 1.8; }
    .person-avatar {
      width: 48px; height: 48px;
      border-radius: 50%;
      background: var(--surface2);
      border: 1px solid var(--border);
      display: flex; align-items: center; justify-content: center;
      font-family: 'Cormorant Garamond', serif;
      font-size: 20px;
      color: var(--accent);
      margin-bottom: 12px;
      overflow: hidden;
    }
    .person-avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

    /* BUTTONS */
    .btn {
      display: inline-block;
      padding: 9px 20px;
      font-family: 'DM Mono', monospace;
      font-size: 11px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }
    .btn-primary { background: var(--accent); color: var(--bg); }
    .btn-primary:hover { background: var(--accent2); color: var(--bg); }
    .btn-ghost { background: transparent; color: var(--muted); border: 1px solid var(--border); }
    .btn-ghost:hover { border-color: var(--accent); color: var(--accent); }
    .btn-danger { background: transparent; color: var(--danger); border: 1px solid var(--danger); }
    .btn-danger:hover { background: var(--danger); color: #fff; }
    .btn-sm { padding: 5px 12px; font-size: 10px; }

    /* FORMS */
    .form-group { margin-bottom: 20px; }
    .form-label {
      display: block;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }
    .form-input, .form-textarea, .form-select {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 14px;
      font-family: 'DM Mono', monospace;
      font-size: 13px;
      outline: none;
      transition: border-color 0.2s;
    }
    .form-input:focus, .form-textarea:focus, .form-select:focus { border-color: var(--accent); }
    .form-textarea { min-height: 100px; resize: vertical; }
    .form-select option { background: var(--surface); }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }

    /* ALERTS */
    .alert {
      padding: 12px 16px;
      margin-bottom: 20px;
      font-size: 12px;
      border-left: 3px solid;
    }
    .alert-success { border-color: var(--success); background: rgba(39,174,96,0.08); color: #6fcf97; }
    .alert-error { border-color: var(--danger); background: rgba(192,57,43,0.08); color: #e57373; }
    .alert-info { border-color: var(--accent); background: rgba(201,168,76,0.08); color: var(--accent); }

    /* TAGS */
    .tag {
      display: inline-block;
      padding: 2px 10px;
      font-size: 10px;
      letter-spacing: 1px;
      text-transform: uppercase;
      border: 1px solid;
    }
    .tag-friend { border-color: #3498db; color: #5dade2; }
    .tag-family { border-color: #e74c3c; color: #ec7063; }
    .tag-colleague { border-color: #27ae60; color: #58d68d; }
    .tag-group { border-color: var(--accent); color: var(--accent); }

    /* STAT BOXES */
    .stats { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
    .stat-box {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 16px 24px;
      min-width: 120px;
    }
    .stat-box .num {
      font-family: 'Cormorant Garamond', serif;
      font-size: 32px;
      color: var(--accent);
      line-height: 1;
    }
    .stat-box .label { font-size: 10px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }

    /* DIVIDER */
    .divider { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
  </style>
</head>
<body>
{% if session.user_id %}
<nav>
  <a href="/dashboard" class="nav-brand">PEOPLE<span>DB</span></a>
  <form class="nav-search" action="/search" method="get">
    <input name="q" placeholder="Search people..." />
    <button type="submit">GO</button>
  </form>
  <div class="nav-links">
    <a href="/dashboard">Directory</a>
    <a href="/person/add">+ Add Person</a>
    <a href="/logout">Logout</a>
  </div>
</nav>
{% endif %}

{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <div style="padding: 0 32px; padding-top: 12px;">
      {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
      {% endfor %}
    </div>
  {% endif %}
{% endwith %}

{% block content %}{% endblock %}
</body>
</html>
'''

TEMPLATES['dashboard.html'] = '''{% extends "base.html" %}
{% block title %}Dashboard — PeopleDB{% endblock %}
{% block content %}
<div class="container">
  <div class="page-header">
    <div class="page-title">
      <small>Your Directory</small>
      People
    </div>
    <a href="/person/add" class="btn btn-primary">+ Add Person</a>
  </div>

  <div class="stats">
    <div class="stat-box">
      <div class="num">{{ total }}</div>
      <div class="label">People</div>
    </div>
  </div>

  {% if people %}
  <div class="card-grid">
    {% for person in people %}
    <a href="/person/{{ person.id }}" style="text-decoration:none; color:inherit;">
      <div class="person-card">
        <div class="person-avatar">
          {% if person.photo_url %}
            <img src="{{ person.photo_url }}" alt="{{ person.name }}"/>
          {% else %}
            {{ person.name[0].upper() }}
          {% endif %}
        </div>
        <h3>{{ person.name }}</h3>
        <div class="meta">
          {% if person.occupation %}📎 {{ person.occupation }}<br>{% endif %}
          {% if person.place_of_birth %}📍 {{ person.place_of_birth }}<br>{% endif %}
          {% if person.dob %}🎂 {{ person.dob.strftime('%d %b %Y') }}<br>{% endif %}
          {% if person.instagram %}📸 @{{ person.instagram }}{% endif %}
        </div>
      </div>
    </a>
    {% endfor %}
  </div>
  {% else %}
  <div class="card" style="text-align:center; padding:60px; color:var(--muted);">
    <div style="font-family:'Cormorant Garamond',serif; font-size:24px; margin-bottom:12px;">No people yet</div>
    <div style="font-size:12px; margin-bottom:24px;">Start building your personal directory</div>
    <a href="/person/add" class="btn btn-primary">Add First Person</a>
  </div>
  {% endif %}
</div>
{% endblock %}
'''

TEMPLATES['view_person.html'] = '''{% extends "base.html" %}
{% block title %}{{ person.name }} — PeopleDB{% endblock %}
{% block content %}
<div class="container">
  <div class="page-header">
    <div class="page-title">
      <small>Profile</small>
      {{ person.name }}
    </div>
    <div style="display:flex;gap:8px;">
      <a href="/person/{{ person.id }}/edit" class="btn btn-ghost">Edit</a>
      <form method="POST" action="/person/{{ person.id }}/delete" onsubmit="return confirm('Delete {{ person.name }}?')">
        <button type="submit" class="btn btn-danger">Delete</button>
      </form>
    </div>
  </div>

  <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">
    <!-- LEFT: Profile -->
    <div>
      <div class="card" style="text-align:center; padding:32px;">
        <div class="person-avatar" style="width:88px;height:88px;font-size:36px;margin:0 auto 16px;">
          {% if person.photo_url %}
            <img src="{{ person.photo_url }}" alt="{{ person.name }}"/>
          {% else %}
            {{ person.name[0].upper() }}
          {% endif %}
        </div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:28px;margin-bottom:4px;">{{ person.name }}</div>
        {% if person.occupation %}<div style="color:var(--muted);font-size:11px;letter-spacing:2px;text-transform:uppercase;">{{ person.occupation }}</div>{% endif %}
      </div>

      <div class="card">
        <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;">Personal Details</div>
        <table style="width:100%;border-collapse:collapse;">
          {% if person.dob %}
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:10px 0;color:var(--muted);font-size:11px;width:40%;">DATE OF BIRTH</td>
            <td style="padding:10px 0;">{{ person.dob.strftime('%d %B %Y') }}</td>
          </tr>
          {% endif %}
          {% if person.place_of_birth %}
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:10px 0;color:var(--muted);font-size:11px;">BIRTHPLACE</td>
            <td style="padding:10px 0;">{{ person.place_of_birth }}</td>
          </tr>
          {% endif %}
          {% if person.school %}
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:10px 0;color:var(--muted);font-size:11px;">SCHOOL</td>
            <td style="padding:10px 0;">{{ person.school }}</td>
          </tr>
          {% endif %}
          {% if person.instagram %}
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:10px 0;color:var(--muted);font-size:11px;">INSTAGRAM</td>
            <td style="padding:10px 0;"><a href="https://instagram.com/{{ person.instagram }}" target="_blank">@{{ person.instagram }}</a></td>
          </tr>
          {% endif %}
          {% if person.phone %}
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:10px 0;color:var(--muted);font-size:11px;">PHONE</td>
            <td style="padding:10px 0;">{{ person.phone }}</td>
          </tr>
          {% endif %}
          {% if person.email %}
          <tr style="border-bottom:1px solid var(--border);">
            <td style="padding:10px 0;color:var(--muted);font-size:11px;">EMAIL</td>
            <td style="padding:10px 0;"><a href="mailto:{{ person.email }}">{{ person.email }}</a></td>
          </tr>
          {% endif %}
          <tr>
            <td style="padding:10px 0;color:var(--muted);font-size:11px;">ADDED</td>
            <td style="padding:10px 0;color:var(--muted);">{{ person.created_at.strftime('%d %b %Y') }}</td>
          </tr>
        </table>
      </div>

      {% if person.notes %}
      <div class="card">
        <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:12px;">Notes</div>
        <div style="line-height:1.8;color:var(--text);">{{ person.notes }}</div>
      </div>
      {% endif %}
    </div>

    <!-- RIGHT: Links -->
    <div>
      <div class="card">
        <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;">Connections</div>

        {% if links %}
        {% for link in links %}
          {% if link.person_a_id == person.id %}
            {% set linked = link.person_b %}
          {% else %}
            {% set linked = link.person_a %}
          {% endif %}
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border);">
            <div style="display:flex;align-items:center;gap:12px;">
              <div class="person-avatar" style="width:36px;height:36px;font-size:14px;flex-shrink:0;">
                {% if linked.photo_url %}
                  <img src="{{ linked.photo_url }}" alt="{{ linked.name }}"/>
                {% else %}
                  {{ linked.name[0].upper() }}
                {% endif %}
              </div>
              <div>
                <a href="/person/{{ linked.id }}" style="color:var(--text);font-size:14px;">{{ linked.name }}</a>
                <div style="margin-top:2px;">
                  <span class="tag tag-{{ link.relation_type }}">{{ link.relation_type }}</span>
                  {% if link.group_name %}<span style="color:var(--muted);font-size:10px;margin-left:6px;">{{ link.group_name }}</span>{% endif %}
                </div>
              </div>
            </div>
            <form method="POST" action="/link/{{ link.id }}/delete">
              <button type="submit" class="btn btn-sm btn-ghost" title="Remove link">✕</button>
            </form>
          </div>
        {% endfor %}
        {% else %}
        <div style="color:var(--muted);font-size:12px;padding:16px 0;">No connections yet.</div>
        {% endif %}
      </div>

      <!-- Add Link Form -->
      <div class="card">
        <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;">Add Connection</div>
        <form method="POST" action="/link/add">
          <input type="hidden" name="person_a_id" value="{{ person.id }}"/>
          <div class="form-group">
            <label class="form-label">Person</label>
            <select name="person_b_id" class="form-select" required>
              <option value="">Select person...</option>
              {% for p in all_people %}
              <option value="{{ p.id }}">{{ p.name }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Relation Type</label>
            <select name="relation_type" class="form-select" required>
              <option value="friend">Friend</option>
              <option value="family">Family</option>
              <option value="colleague">Colleague</option>
              <option value="group">Group</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Group / Label (optional)</label>
            <input type="text" name="group_name" class="form-input" placeholder="e.g. College Friends, School Batch 2019"/>
          </div>
          <button type="submit" class="btn btn-primary btn-sm">Link Person</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
'''

TEMPLATES['add_person.html'] = '''{% extends "base.html" %}
{% block title %}{% if person %}Edit {{ person.name }}{% else %}Add Person{% endif %} — PeopleDB{% endblock %}
{% block content %}
<div class="container">
  <div class="page-header">
    <div class="page-title">
      <small>{% if person %}Editing{% else %}New Entry{% endif %}</small>
      {% if person %}{{ person.name }}{% else %}Add Person{% endif %}
    </div>
    <a href="/dashboard" class="btn btn-ghost">← Back</a>
  </div>

  <form method="POST">
    <div class="card">
      <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:20px;">Basic Info</div>
      <div class="form-grid">
        <div class="form-group" style="grid-column:1/-1;">
          <label class="form-label">Full Name *</label>
          <input type="text" name="name" class="form-input" required value="{{ person.name if person else '' }}" placeholder="Enter full name"/>
        </div>
        <div class="form-group">
          <label class="form-label">Date of Birth</label>
          <input type="date" name="dob" class="form-input" value="{{ person.dob.strftime('%Y-%m-%d') if person and person.dob else '' }}"/>
        </div>
        <div class="form-group">
          <label class="form-label">Place of Birth</label>
          <input type="text" name="place_of_birth" class="form-input" value="{{ person.place_of_birth or '' }}" placeholder="City, Country"/>
        </div>
        <div class="form-group">
          <label class="form-label">School / College</label>
          <input type="text" name="school" class="form-input" value="{{ person.school or '' }}" placeholder="School or university"/>
        </div>
        <div class="form-group">
          <label class="form-label">Occupation</label>
          <input type="text" name="occupation" class="form-input" value="{{ person.occupation or '' }}" placeholder="Job title / role"/>
        </div>
      </div>
    </div>

    <div class="card">
      <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:20px;">Contact & Social</div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Instagram Username</label>
          <input type="text" name="instagram" class="form-input" value="{{ person.instagram or '' }}" placeholder="username (no @)"/>
        </div>
        <div class="form-group">
          <label class="form-label">Phone</label>
          <input type="text" name="phone" class="form-input" value="{{ person.phone or '' }}" placeholder="+91 ..."/>
        </div>
        <div class="form-group">
          <label class="form-label">Email</label>
          <input type="email" name="email" class="form-input" value="{{ person.email or '' }}" placeholder="email@example.com"/>
        </div>
        <div class="form-group">
          <label class="form-label">Photo URL</label>
          <input type="url" name="photo_url" class="form-input" value="{{ person.photo_url or '' }}" placeholder="https://..."/>
        </div>
      </div>
    </div>

    <div class="card">
      <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:20px;">Notes</div>
      <div class="form-group">
        <label class="form-label">Personal Notes</label>
        <textarea name="notes" class="form-textarea" placeholder="Anything you want to remember about this person...">{{ person.notes or '' }}</textarea>
      </div>
    </div>

    <div style="display:flex;gap:12px;justify-content:flex-end;">
      <a href="/dashboard" class="btn btn-ghost">Cancel</a>
      <button type="submit" class="btn btn-primary">{% if person %}Save Changes{% else %}Add to Directory{% endif %}</button>
    </div>
  </form>
</div>
{% endblock %}
'''

TEMPLATES['search.html'] = '''{% extends "base.html" %}
{% block title %}Search — PeopleDB{% endblock %}
{% block content %}
<div class="container">
  <div class="page-header">
    <div class="page-title">
      <small>Search Results</small>
      "{{ query }}"
    </div>
    <a href="/dashboard" class="btn btn-ghost">← Back</a>
  </div>

  {% if results %}
  <div style="color:var(--muted);font-size:11px;margin-bottom:20px;letter-spacing:1px;">{{ results|length }} result(s) found</div>
  <div class="card-grid">
    {% for person in results %}
    <a href="/person/{{ person.id }}" style="text-decoration:none;color:inherit;">
      <div class="person-card">
        <div class="person-avatar">
          {% if person.photo_url %}<img src="{{ person.photo_url }}" alt="{{ person.name }}"/>{% else %}{{ person.name[0].upper() }}{% endif %}
        </div>
        <h3>{{ person.name }}</h3>
        <div class="meta">
          {% if person.occupation %}📎 {{ person.occupation }}<br>{% endif %}
          {% if person.place_of_birth %}📍 {{ person.place_of_birth }}<br>{% endif %}
          {% if person.dob %}🎂 {{ person.dob.strftime('%d %b %Y') }}{% endif %}
        </div>
      </div>
    </a>
    {% endfor %}
  </div>
  {% elif query %}
  <div class="card" style="text-align:center;padding:48px;color:var(--muted);">
    <div style="font-family:'Cormorant Garamond',serif;font-size:22px;margin-bottom:8px;">No results for "{{ query }}"</div>
    <a href="/person/add" class="btn btn-primary" style="margin-top:16px;">Add This Person</a>
  </div>
  {% endif %}
</div>
{% endblock %}
'''

def render(template_name, **kwargs):
    # Inline base template expansion
    content = TEMPLATES[template_name]
    if '{% extends "base.html" %}' in content:
        block_content = ''
        if '{% block content %}' in content:
            block_content = content.split('{% block content %}')[1].split('{% endblock %}')[0]
        block_title = ''
        if '{% block title %}' in content:
            block_title = content.split('{% block title %}')[1].split('{% endblock %}')[0]
        base = TEMPLATES['base.html']
        base = base.replace('{% block title %}PeopleDB{% endblock %}', block_title if block_title else 'PeopleDB')
        base = base.replace('{% block content %}{% endblock %}', block_content)
        content = base
    return render_template_string(content, **kwargs)

# ── ROUTES ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    people = Person.query.order_by(Person.name).all()
    total = Person.query.count()
    return render('dashboard.html', people=people, total=total)

@app.route('/person/add', methods=['GET', 'POST'])
@login_required
def add_person():
    if request.method == 'POST':
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        person = Person(
            name=request.form.get('name'),
            dob=dob,
            place_of_birth=request.form.get('place_of_birth'),
            school=request.form.get('school'),
            instagram=request.form.get('instagram'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            occupation=request.form.get('occupation'),
            notes=request.form.get('notes'),
            photo_url=request.form.get('photo_url'),
            added_by=session['user_id']
        )
        db.session.add(person)
        db.session.commit()
        flash(f'{person.name} added successfully!', 'success')
        return redirect(url_for('view_person', person_id=person.id))
    return render('add_person.html', person=None)

@app.route('/person/<int:person_id>')
@login_required
def view_person(person_id):
    person = Person.query.get_or_404(person_id)
    links = Link.query.filter(
        (Link.person_a_id == person_id) | (Link.person_b_id == person_id)
    ).all()
    all_people = Person.query.filter(Person.id != person_id).all()
    return render('view_person.html', person=person, links=links, all_people=all_people)

@app.route('/person/<int:person_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_person(person_id):
    person = Person.query.get_or_404(person_id)
    if request.method == 'POST':
        dob_str = request.form.get('dob')
        person.dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        person.name = request.form.get('name')
        person.place_of_birth = request.form.get('place_of_birth')
        person.school = request.form.get('school')
        person.instagram = request.form.get('instagram')
        person.phone = request.form.get('phone')
        person.email = request.form.get('email')
        person.occupation = request.form.get('occupation')
        person.notes = request.form.get('notes')
        person.photo_url = request.form.get('photo_url')
        db.session.commit()
        flash('Updated successfully!', 'success')
        return redirect(url_for('view_person', person_id=person.id))
    return render('add_person.html', person=person)

@app.route('/person/<int:person_id>/delete', methods=['POST'])
@login_required
def delete_person(person_id):
    person = Person.query.get_or_404(person_id)
    Link.query.filter(
        (Link.person_a_id == person_id) | (Link.person_b_id == person_id)
    ).delete()
    db.session.delete(person)
    db.session.commit()
    flash('Person deleted.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/link/add', methods=['POST'])
@login_required
def add_link():
    person_a_id = int(request.form.get('person_a_id'))
    person_b_id = int(request.form.get('person_b_id'))
    relation_type = request.form.get('relation_type')
    group_name = request.form.get('group_name', '')
    existing = Link.query.filter(
        ((Link.person_a_id == person_a_id) & (Link.person_b_id == person_b_id)) |
        ((Link.person_a_id == person_b_id) & (Link.person_b_id == person_a_id))
    ).first()
    if not existing:
        link = Link(person_a_id=person_a_id, person_b_id=person_b_id,
                    relation_type=relation_type, group_name=group_name)
        db.session.add(link)
        db.session.commit()
        flash('Link added!', 'success')
    else:
        flash('Already linked.', 'info')
    return redirect(url_for('view_person', person_id=person_a_id))

@app.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    person_id = link.person_a_id
    db.session.delete(link)
    db.session.commit()
    return redirect(url_for('view_person', person_id=person_id))

@app.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    results = Person.query.filter(Person.name.ilike(f'%{q}%')).all() if q else []
    return render('search.html', results=results, query=q)

# ── INIT ────────────────────────────────────────────────────────────────────

def create_tables():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

create_tables()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
