"""Google Drive Service - Sparar PDF-kopior av newsletters"""

import os
import json
from io import BytesIO
from xhtml2pdf import pisa
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveService:
    def __init__(self):
        self.service = self._authenticate()
        self.parent_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    def _authenticate(self):
        """Autentisera med Drive API"""
        credentials_json = os.getenv('GMAIL_CREDENTIALS')  # Samma credentials
        credentials_dict = json.loads(credentials_json)
        
        if 'refresh_token' in credentials_dict:
            creds = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        return build('drive', 'v3', credentials=creds)
    
    def create_weekly_folder(self, folder_name):
        """Skapa veckomapp om den inte finns"""
        # Kolla om mappen redan finns
        query = f"name='{folder_name}' and '{self.parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        # Skapa ny mapp
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.parent_folder_id]
        }
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        # Gör mappen delbar (anyone with link can view)
        self.service.permissions().create(
            fileId=folder['id'],
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        return folder['id']
    
    def save_newsletter(self, newsletter, folder_id):
        """Spara newsletter som PDF-fil"""
        # Skapa filnamn (säkert för filsystem)
        safe_subject = "".join(c for c in newsletter['subject'] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_subject = safe_subject[:50]  # Begränsa längd
        filename = f"{safe_subject}.pdf"
        
        try:
            # Konvertera HTML till PDF med xhtml2pdf
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(
                BytesIO(newsletter['html_body'].encode('utf-8')),
                dest=pdf_buffer
            )
            
            if pisa_status.err:
                raise Exception(f"PDF conversion error: {pisa_status.err}")
            
            pdf_buffer.seek(0)
            
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
            
            return {
                'id': file['id'],
                'url': file['webViewLink']
            }
            
        except Exception as e:
            print(f"Fel vid PDF-konvertering för {safe_subject}: {e}")
            # Fallback - spara som text om PDF misslyckas
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
        
        # Använd snippet istället för HTML
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
