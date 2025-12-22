"""Supabase Service - Lagrar metadata och historik"""

import os
from supabase import create_client, Client
from datetime import datetime

class SupabaseService:
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        # Debug
        print(f"DEBUG - SUPABASE_URL: {url}")
        print(f"DEBUG - SUPABASE_KEY exists: {key is not None}")
        print(f"DEBUG - SUPABASE_KEY length: {len(key) if key else 0}")
        
        self.client: Client = create_client(url, key)
    
    def save_weekly_summary(self, week, markdown_content, newsletters, youtube_picks):
        """Spara eller uppdatera veckosammanfattning"""
        try:
            # Kolla om veckan redan finns
            existing = self.client.table('weekly_summaries').select('id').eq('week', week).execute()
            
            summary_data = {
                'week': week,
                'created_at': datetime.now().isoformat(),
                'markdown_content': markdown_content,
                'status': 'completed',
                'newsletter_count': len(newsletters)
            }
            
            if existing.data:
                # Uppdatera befintlig
                summary_id = existing.data[0]['id']
                self.client.table('weekly_summaries').update(summary_data).eq('id', summary_id).execute()
                
                # Ta bort gamla newsletters för denna vecka
                self.client.table('newsletters').delete().eq('summary_id', summary_id).execute()
            else:
                # Skapa ny
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
