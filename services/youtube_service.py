"""YouTube Service - Hämtar videolista från Supabase"""

import os
from supabase import create_client, Client

class YouTubeService:
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        self.client: Client = create_client(url, key)
    
    def get_videos(self):
        """Hämta alla aktiva videos från Supabase"""
        try:
            result = self.client.table('youtube_videos').select('*').eq('is_active', True).execute()
            return result.data
        except Exception as e:
            print(f"Fel vid hämtning från Supabase: {e}")
            return []
