"""
AI Newsletter Weekly Summary Generator
Körs varje fredag kl 08:00 via Railway Cron
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from services.gmail_service import GmailService
from services.drive_service import DriveService
from services.youtube_service import YouTubeService
from services.claude_service import ClaudeService
from services.supabase_service import SupabaseService
from services.email_service import EmailService
from utils.logger import setup_logger

logger = setup_logger()

def main():
    """Huvudflöde för veckosammanfattning"""
    try:
        print("DEBUG: main() started", flush=True)
        logger.info("=== Startar veckosammanfattning ===")
        
        # Initialisera services
        print("DEBUG: Initializing services", flush=True)
        gmail = GmailService()
        print("DEBUG: Gmail service OK", flush=True)
        drive = DriveService()
        print("DEBUG: Drive service OK", flush=True)
        youtube = YouTubeService()
        print("DEBUG: YouTube service OK", flush=True)
        claude = ClaudeService()
        print("DEBUG: Claude service OK", flush=True)
        supabase = SupabaseService()
        print("DEBUG: Supabase service OK", flush=True)
        email_service = EmailService()
        print("DEBUG: Email service OK", flush=True)
        
        # 1. Hämta newsletters från senaste veckan
        logger.info("Hämtar newsletters från Gmail...")
        print("DEBUG: Fetching newsletters", flush=True)
        newsletters = gmail.get_newsletters_last_week()
        logger.info(f"Hittade {len(newsletters)} newsletters")
        
        if not newsletters:
            logger.warning("Inga newsletters hittades - avslutar")
            return
        
        # 2. Skapa veckomapp på Drive
        week_number = datetime.now().isocalendar()[1]
        year = datetime.now().year
        folder_name = f"{year}-W{week_number:02d}"
        logger.info(f"Skapar mapp på Drive: {folder_name}")
        folder_id = drive.create_weekly_folder(folder_name)
        
        # 3. Spara newsletters till Drive
        logger.info("Sparar newsletters till Drive...")
        saved_newsletters = []
        for newsletter in newsletters:
            try:
                file_info = drive.save_newsletter(newsletter, folder_id)
                saved_newsletters.append({
                    **newsletter,
                    'drive_url': file_info['url'],
                    'drive_id': file_info['id']
                })
            except Exception as e:
                logger.error(f"Kunde inte spara newsletter: {e}")
                continue
        
        logger.info(f"Sparade {len(saved_newsletters)} newsletters till Drive")
        
        # 4. Hämta YouTube-lista
        logger.info("Hämtar YouTube-lista...")
        youtube_videos = youtube.get_videos()
        logger.info(f"Hämtade {len(youtube_videos)} YouTube-videos")
        
        # 5. AI-analys med Claude
        logger.info("Analyserar med Claude...")
        analysis = claude.analyze_week(saved_newsletters, youtube_videos)
        
        # 6. Spara till Supabase
        logger.info("Sparar till Supabase...")
        summary_id = supabase.save_weekly_summary(
            week=folder_name,
            markdown_content=analysis['markdown'],
            newsletters=saved_newsletters,
            youtube_picks=analysis['youtube_picks']
        )
        
        # 7. Skicka email med färdigt Markdown
        logger.info("Skickar email...")
        email_service.send_summary(
            to_email=os.getenv('EMAIL_TO'),
            subject=f"AI-sammanfattning vecka {week_number}",
            markdown=analysis['markdown'],
            week=folder_name
        )
        
        # 8. Markera newsletters som lästa
        logger.info("Markerar newsletters som lästa...")
        newsletter_ids = [nl['id'] for nl in newsletters]
        gmail.mark_as_read(newsletter_ids)
        
        logger.info("=== Klart! ===")
        logger.info(f"Sammanfattning sparad med ID: {summary_id}")
        
    except Exception as e:
        logger.error(f"Fel i huvudflöde: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
