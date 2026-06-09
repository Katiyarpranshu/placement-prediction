import sqlite3
import pandas as pd
from datetime import datetime
import os

class DataProcessor:
    def __init__(self, db_path='database/placement.db'):
        self.db_path = db_path
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
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
        
        conn.commit()
        conn.close()
    
    def save_prediction(self, prediction_data):
        """Save a prediction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (student_name, date, bachelor_percentage, mca_percentage, backlogs, 
             communication_score, aptitude_score, coding_skills, internship_done, 
             projects_done, prediction_result, probability, improvement_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', prediction_data)
        
        conn.commit()
        conn.close()
    
    def get_predictions_history(self, student_name=None):
        """Get prediction history for a student"""
        conn = sqlite3.connect(self.db_path)
        
        if student_name:
            query = "SELECT * FROM predictions WHERE student_name = ? ORDER BY date DESC"
            df = pd.read_sql_query(query, conn, params=(student_name,))
        else:
            df = pd.read_sql_query("SELECT * FROM predictions ORDER BY date DESC", conn)
        
        conn.close()
        return df
    
    def get_historical_data(self):
        """Get all historical data for peer comparison"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM historical_data", conn)
        conn.close()
        return df
    
    def calculate_peer_stats(self):
        """Calculate peer statistics for comparison"""
        conn = sqlite3.connect(self.db_path)
        
        # Check if historical_data has data
        try:
            df = pd.read_sql_query("SELECT * FROM historical_data", conn)
        except:
            # Table doesn't exist yet
            conn.close()
            return self._get_default_stats()
        
        conn.close()
        
        if len(df) == 0:
            return self._get_default_stats()
        
        metrics = ['bachelor_percentage', 'mca_percentage', 'communication_score', 
                  'aptitude_score', 'coding_skills', 'projects_done']
        
        peer_stats = {}
        for metric in metrics:
            if metric in df.columns:
                peer_stats[metric] = {
                    'mean': df[metric].mean(),
                    'median': df[metric].median(),
                    'percentile_25': df[metric].quantile(0.25),
                    'percentile_75': df[metric].quantile(0.75),
                    'std': df[metric].std()
                }
            else:
                peer_stats[metric] = {
                    'mean': 70,
                    'median': 70,
                    'percentile_25': 60,
                    'percentile_75': 80,
                    'std': 10
                }
        
        peer_stats['placement_rate'] = df['placed'].mean() * 100 if 'placed' in df.columns else 70
        
        return peer_stats
    
    def _get_default_stats(self):
        """Return default statistics when no data available"""
        return {
            'bachelor_percentage': {'mean': 70, 'median': 70, 'percentile_25': 60, 'percentile_75': 80, 'std': 10},
            'mca_percentage': {'mean': 75, 'median': 75, 'percentile_25': 65, 'percentile_75': 85, 'std': 10},
            'communication_score': {'mean': 7, 'median': 7, 'percentile_25': 6, 'percentile_75': 8, 'std': 2},
            'aptitude_score': {'mean': 6, 'median': 6, 'percentile_25': 5, 'percentile_75': 7, 'std': 2},
            'coding_skills': {'mean': 7, 'median': 7, 'percentile_25': 6, 'percentile_75': 8, 'std': 2},
            'projects_done': {'mean': 2.5, 'median': 2, 'percentile_25': 1, 'percentile_75': 4, 'std': 1.5},
            'placement_rate': 70
        }
    
    def compare_with_peers(self, student_data):
        """Compare a student's metrics with peer averages"""
        peer_stats = self.calculate_peer_stats()
        
        comparison = {}
        for metric, value in student_data.items():
            if metric in peer_stats:
                stats = peer_stats[metric]
                comparison[metric] = {
                    'student_value': value,
                    'peer_average': round(stats['mean'], 2),
                    'percentile': round((value - stats['mean']) / stats['std'] * 10 + 50, 1) if stats['std'] > 0 else 50,
                    'better_than_peers': value > stats['mean'],
                    'difference': round(value - stats['mean'], 2)
                }
        
        return comparison