"""Gmail Service - Hämtar newsletters med label 'Newsletters'"""

import os
import base64
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailService:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Autentisera med Gmail API"""
        creds = None
        credentials_json = os.getenv('GMAIL_CREDENTIALS')
        
        if not credentials_json:
            raise ValueError("GMAIL_CREDENTIALS saknas i environment variables")
        
        credentials_dict = json.loads(credentials_json)
        
        # För Railway: använd service account eller OAuth refresh token
        # Här antar vi att vi har en refresh token
        if 'refresh_token' in credentials_dict:
            creds = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        
        return build('gmail', 'v1', credentials=creds)
    
    def get_newsletters_last_week(self):
        """Hämta newsletters från förra fredagen 08:00 till denna fredagen 08:00"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Räkna ut förra fredagen kl 08:00
        days_since_friday = (now.weekday() - 4) % 7  # Fredag = 4
        last_friday = now - timedelta(days=days_since_friday + 7)
        last_friday = last_friday.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Till och med denna fredagen kl 08:00
        this_friday = now.replace(hour=8, minute=0, second=0, microsecond=0)
        
        query = f'label:Newsletters after:{last_friday.strftime("%Y/%m/%d")} before:{this_friday.strftime("%Y/%m/%d")} is:unread'
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            newsletters = []
            
            for msg in messages:
                newsletter = self._get_message_details(msg['id'])
                if newsletter:
                    newsletters.append(newsletter)
            
            return newsletters
            
        except Exception as e:
            print(f"Fel vid hämtning från Gmail: {e}")
            return []
    
    def mark_as_read(self, message_ids):
        """Markera newsletters som lästa efter bearbetning"""
        try:
            for msg_id in message_ids:
                self.service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            print(f"✓ Markerade {len(message_ids)} newsletters som lästa")
        except Exception as e:
            print(f"Fel vid markering som läst: {e}")
    
    def _get_message_details(self, msg_id):
        """Hämta detaljer för ett specifikt meddelande"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Ingen titel')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Okänd')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Hämta HTML-body
            html_body = self._get_html_body(message['payload'])
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'html_body': html_body,
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            print(f"Fel vid hämtning av meddelande {msg_id}: {e}")
            return None
    
    def _get_html_body(self, payload):
        """Extrahera HTML-body från meddelande"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    # Rekursivt för nested parts
                    html = self._get_html_body(part)
                    if html:
                        return html
        
        # Fallback till body direkt
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return ""
