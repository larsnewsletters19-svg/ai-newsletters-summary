"""Google Drive Service - Sparar HTML-kopior av newsletters"""

import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

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
        """Spara newsletter som HTML-fil"""
        # Skapa filnamn (säkert för filsystem)
        safe_subject = "".join(c for c in newsletter['subject'] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_subject = safe_subject[:50]  # Begränsa längd
        filename = f"{safe_subject}.html"
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'text/html'
        }
        
        media = MediaInMemoryUpload(
            newsletter['html_body'].encode('utf-8'),
            mimetype='text/html',
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
