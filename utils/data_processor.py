import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3

class DataProcessor:
    def __init__(self, db_path='database/placement.db'):
        self.db_path = db_path
    
    def save_prediction(self, student_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (student_name, date, bachelor_percentage, mca_percentage, backlogs, 
             communication_score, aptitude_score, coding_skills, internship_done, 
             projects_done, prediction_result, probability, improvement_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', student_data)
        
        conn.commit()
        conn.close()
    
    def get_historical_data(self, student_name=None):
        conn = sqlite3.connect(self.db_path)
        
        if student_name:
            query = "SELECT * FROM historical_data WHERE student_name = ? ORDER BY date DESC"
            df = pd.read_sql_query(query, conn, params=(student_name,))
        else:
            df = pd.read_sql_query("SELECT * FROM historical_data ORDER BY date DESC", conn)
        
        conn.close()
        return df
    
    def get_predictions_history(self, student_name=None):
        conn = sqlite3.connect(self.db_path)
        
        if student_name:
            query = "SELECT * FROM predictions WHERE student_name = ? ORDER BY date DESC"
            df = pd.read_sql_query(query, conn, params=(student_name,))
        else:
            df = pd.read_sql_query("SELECT * FROM predictions ORDER BY date DESC", conn)
        
        conn.close()
        return df
    
    def calculate_peer_stats(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM historical_data", conn)
        conn.close()
        
        metrics = ['bachelor_percentage', 'mca_percentage', 'communication_score', 
                  'aptitude_score', 'coding_skills', 'projects_done']
        
        peer_stats = {}
        for metric in metrics:
            peer_stats[metric] = {
                'mean': df[metric].mean(),
                'median': df[metric].median(),
                'percentile_25': df[metric].quantile(0.25),
                'percentile_75': df[metric].quantile(0.75),
                'std': df[metric].std()
            }
        
        # Placement rate
        peer_stats['placement_rate'] = df['placed'].mean() * 100
        
        return peer_stats
    
    def compare_with_peers(self, student_data):
        peer_stats = self.calculate_peer_stats()
        
        comparison = {}
        for metric, value in student_data.items():
            if metric in peer_stats:
                stats = peer_stats[metric]
                percentile_rank = (value - stats['mean']) / stats['std']
                
                comparison[metric] = {
                    'student_value': value,
                    'peer_average': round(stats['mean'], 2),
                    'percentile': round((value - stats['mean']) / stats['std'] * 10 + 50, 1),
                    'better_than_peers': value > stats['mean'],
                    'difference': round(value - stats['mean'], 2)
                }
        
        return comparison