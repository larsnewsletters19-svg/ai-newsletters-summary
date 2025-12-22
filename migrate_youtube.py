"""
Migrera YouTube-videos från Excel till Supabase
Kör detta en gång för att importera din befintliga data
"""

import openpyxl
import os
from supabase import create_client

def migrate_youtube_videos(excel_file):
    """Migrera videos från Excel till Supabase"""
    
    # Läs Supabase credentials från .env
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ SUPABASE_URL och SUPABASE_KEY måste vara satta")
        print("Kör: export SUPABASE_URL=... && export SUPABASE_KEY=...")
        return
    
    client = create_client(url, key)
    
    # Läs Excel-fil
    wb = openpyxl.load_workbook(excel_file)
    ws = wb.active
    
    videos_added = 0
    errors = 0
    
    print("🔄 Migrerar videos från Excel till Supabase...")
    
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or len(row) < 3:
            continue
        
        video_data = {
            'title': row[1] if len(row) > 1 else '',
            'url': row[2] if len(row) > 2 else '',
            'category': row[3] if len(row) > 3 else '',
            'type': row[4] if len(row) > 4 else '',
            'description': row[6] if len(row) > 6 else '',
            'is_active': True
        }
        
        if not video_data['title'] or not video_data['url']:
            continue
        
        try:
            client.table('youtube_videos').insert(video_data).execute()
            print(f"✓ Rad {i}: {video_data['title']}")
            videos_added += 1
        except Exception as e:
            print(f"✗ Rad {i}: {e}")
            errors += 1
    
    print(f"\n✅ Klart! {videos_added} videos tillagda, {errors} fel")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Användning: python migrate_youtube.py <excel_fil>")
        print("Exempel: python migrate_youtube.py Videolänkar.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"❌ Filen {excel_file} hittas inte")
        sys.exit(1)
    
    migrate_youtube_videos(excel_file)
