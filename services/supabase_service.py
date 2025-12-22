"""Supabase Service - Lagrar metadata och historik"""

import os
from supabase import create_client, Client
from datetime import datetime

class SupabaseService:
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        self.client: Client = create_client(url, key)
    
    def save_weekly_summary(self, week, markdown_content, newsletters, youtube_picks):
        """Spara veckosammanfattning"""
        try:
            # Spara huvudsammanfattning
            summary_data = {
                'week': week,
                'created_at': datetime.now().isoformat(),
                'markdown_content': markdown_content,
                'status': 'completed',
                'newsletter_count': len(newsletters)
            }
            
            result = self.client.table('weekly_summaries').insert(summary_data).execute()
            summary_id = result.data[0]['id']
            
            # Spara newsletter metadata
            for nl in newsletters:
                newsletter_data = {
                    'summary_id': summary_id,
                    'week': week,
                    'title': nl['subject'],
                    'from_email': nl['from'],
                    'date': nl['date'],
                    'drive_url': nl['drive_url'],
                    'snippet': nl['snippet']
                }
                self.client.table('newsletters').insert(newsletter_data).execute()
            
            return summary_id
            
        except Exception as e:
            print(f"Fel vid sparning till Supabase: {e}")
            raise
    
    def get_summary_by_week(self, week):
        """Hämta sammanfattning för specifik vecka"""
        result = self.client.table('weekly_summaries').select('*').eq('week', week).execute()
        return result.data[0] if result.data else None
    
    def get_all_summaries(self, limit=10):
        """Hämta senaste sammanfattningar"""
        result = self.client.table('weekly_summaries').select('*').order('created_at', desc=True).limit(limit).execute()
        return result.data
