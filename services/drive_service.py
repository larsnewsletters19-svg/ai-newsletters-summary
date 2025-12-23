"""Google Drive Service - Sparar PDF-kopior av newsletters med Playwright"""

import os
import json
from io import BytesIO
from playwright.sync_api import sync_playwright
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveService:
    def __init__(self):
        self.service = self._authenticate()
        self.parent_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        self.playwright = None
        self.browser = None
    
    def __del__(self):
        """Cleanup Playwright resources"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _authenticate(self):
        """Autentisera med Drive API"""
        credentials_json = os.getenv('GMAIL_CREDENTIALS')
        credentials_dict = json.loads(credentials_json)
        
        if 'refresh_token' in credentials_dict:
            creds = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        return build('drive', 'v3', credentials=creds)
    
    def _get_browser(self):
        """Lazy load Playwright browser"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
        return self.browser
    
    def create_weekly_folder(self, folder_name):
        """Skapa veckomapp om den inte finns"""
        query = f"name='{folder_name}' and '{self.parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.parent_folder_id]
        }
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        self.service.permissions().create(
            fileId=folder['id'],
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        return folder['id']
    
    def save_newsletter(self, newsletter, folder_id):
        """Spara newsletter som PDF med Playwright"""
        safe_subject = "".join(c for c in newsletter['subject'] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_subject = safe_subject[:50]
        filename = f"{safe_subject}.pdf"
        
        try:
            print(f"Converting {safe_subject} to PDF with Playwright...")
            
            browser = self._get_browser()
            page = browser.new_page()
            
            # Ladda HTML
            page.set_content(newsletter['html_body'], wait_until='networkidle')
            
            # Generera PDF
            pdf_bytes = page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '20px', 'right': '20px', 'bottom': '20px', 'left': '20px'}
            )
            
            page.close()
            
            # Ladda upp till Drive
            pdf_buffer = BytesIO(pdf_bytes)
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': 'application/pdf'
            }
            
            media = MediaIoBaseUpload(
                pdf_buffer,
                mimetype='application/pdf',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            print(f"✓ PDF created: {filename}")
            
            return {
                'id': file['id'],
                'url': file['webViewLink']
            }
            
        except Exception as e:
            print(f"Fel vid PDF-konvertering för {safe_subject}: {e}")
            return self._save_as_text_fallback(newsletter, folder_id, safe_subject)
    
    def _save_as_text_fallback(self, newsletter, folder_id, safe_subject):
        """Fallback: Spara som text om PDF misslyckas"""
        from googleapiclient.http import MediaInMemoryUpload
        
        filename = f"{safe_subject}.txt"
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'text/plain'
        }
        
        content = f"Subject: {newsletter['subject']}\nFrom: {newsletter['from']}\n\n{newsletter['snippet']}"
        
        media = MediaInMemoryUpload(
            content.encode('utf-8'),
            mimetype='text/plain',
            resumable=True
        )
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return {
            'id': file['id'],
            'url': file['webViewLink']
        }
