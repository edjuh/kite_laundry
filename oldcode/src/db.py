import sqlite3
import os
import yaml
import json
from datetime import datetime
import logging

def init_db():
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS designs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  type TEXT NOT NULL,
                  dimensions TEXT NOT NULL,
                  colors TEXT NOT NULL,
                  rod TEXT,
                  creation_date TEXT NOT NULL,
                  unit_label TEXT DEFAULT 'cm')''')
    c.execute('''PRAGMA table_info(designs)''')
    columns = [info[1] for info in c.fetchall()]
    if 'unit_label' not in columns:
        c.execute('''ALTER TABLE designs ADD COLUMN unit_label TEXT DEFAULT 'cm' ''')
    c.execute('''UPDATE designs SET unit_label = 'cm' WHERE unit_label IS NULL''')
    conn.commit()
    resource_dir = 'projects/resources'
    if os.path.exists(resource_dir):
        for yaml_file in os.listdir(resource_dir):
            if yaml_file.endswith('.yaml'):
                with open(os.path.join(resource_dir, yaml_file), 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'name' in data and 'type' in data:
                        c.execute('INSERT OR IGNORE INTO designs (name, type, dimensions, colors, rod, creation_date, unit_label) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                  (data['name'], data['type'], json.dumps(data.get('dimensions', {})), json.dumps(data.get('colors', [])), data.get('rod', 'none'), data.get('creation_date', datetime.now().isoformat()), 'cm'))
                    conn.commit()
    conn.close()

def get_design_by_name(name):
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM designs WHERE name = ? ORDER BY id DESC LIMIT 1', (name,))
    design = c.fetchone()
    conn.close()
    return design

def save_design(name, design_type, dimensions, colors, rod, units):
    conn = sqlite3.connect('designs.db')
    c = conn.cursor()
    c.execute('INSERT INTO designs (name, type, dimensions, colors, rod, creation_date, unit_label) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (name, design_type, json.dumps(dimensions), json.dumps(colors), rod, datetime.now().isoformat(), units))
    conn.commit()
    conn.close()
    logging.info(f'Saved design: {name}')

init_db()
