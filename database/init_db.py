import sqlite3
import pandas as pd
from datetime import datetime

def init_database():
    conn = sqlite3.connect('database/placement.db')
    cursor = conn.cursor()
    
    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            date TIMESTAMP,
            bachelor_percentage REAL,
            mca_percentage REAL,
            backlogs INTEGER,
            communication_score INTEGER,
            aptitude_score INTEGER,
            coding_skills INTEGER,
            internship_done INTEGER,
            projects_done INTEGER,
            prediction_result INTEGER,
            probability REAL,
            improvement_points TEXT
        )
    ''')
    
    # Create historical_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            date TIMESTAMP,
            bachelor_percentage REAL,
            mca_percentage REAL,
            backlogs INTEGER,
            communication_score INTEGER,
            aptitude_score INTEGER,
            coding_skills INTEGER,
            internship_done INTEGER,
            projects_done INTEGER,
            placed INTEGER
        )
    ''')
    
    # Create peer_comparison table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peer_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            average_value REAL,
            percentile_25 REAL,
            percentile_50 REAL,
            percentile_75 REAL,
            updated_date TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_database()