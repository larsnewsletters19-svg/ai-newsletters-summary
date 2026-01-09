"""Email Service - Skickar färdig sammanfattning via Gmail API"""

import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailService:
    def __init__(self):
        self.service = self._authenticate()
        self.from_email = os.getenv('EMAIL_FROM', 'lars.newsletters19@gmail.com')
    
    def _authenticate(self):
        """Autentisera med Gmail API"""
        credentials_json = os.getenv('GMAIL_CREDENTIALS')
        
        if not credentials_json:
            raise ValueError("GMAIL_CREDENTIALS saknas")
        
        credentials_dict = json.loads(credentials_json)
        
        if 'refresh_token' in credentials_dict:
            creds = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        return build('gmail', 'v1', credentials=creds)
    
    def send_summary(self, to_email, subject, markdown, week):
        """Skicka veckosammanfattning via Gmail API"""
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        
        # Text version
        text_body = f"""
AI-veckosammanfattning för {week}

Här är din färdiga Markdown-sammanfattning redo att kopiera till Teams!

{'='*60}

{markdown}

{'='*60}

Kopiera allt ovanför denna rad och klistra in i Teams.
Markdown kommer automatiskt att formateras snyggt!
"""
        
        # HTML version
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h2>🤖 AI-veckosammanfattning för {week}</h2>
    <p>Här är din färdiga Markdown-sammanfattning redo att kopiera till Teams!</p>
    
    <div style="background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin: 20px 0;">
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: 'Courier New', monospace;">{markdown}</pre>
    </div>
    
    <p><strong>Instruktioner:</strong></p>
    <ol>
        <li>Kopiera allt i den grå rutan ovan</li>
        <li>Öppna Teams och gå till din kanal</li>
        <li>Klistra in i ett nytt inlägg</li>
        <li>Markdown formateras automatiskt snyggt i Teams!</li>
    </ol>
</body>
</html>
"""
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            # Skapa raw message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Skicka via Gmail API
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✓ Email skickat till {to_email} via Gmail API")
            
        except Exception as e:
            print(f"Fel vid emailsändning: {e}")
            raise
    
    def send_teams_post(self, to_email, subject, short_description, week):
        """Skicka kort Teams-inlägg via Gmail API"""
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        
        # Text version
        text_body = f"""
Teams-inlägg för vecka {week}

Kopiera texten nedan och klistra in som ett nytt inlägg i din Teams-kanal:

{'='*60}

{short_description}

{'='*60}

Detta korta inlägg berättar för teamet att det finns en ny sammanfattning.
Den fullständiga sammanfattningen ska kopieras till Teams-fliken.
"""
        
        # HTML version
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h2>📢 Teams-inlägg för vecka {week}</h2>
    <p>Kopiera texten nedan och klistra in som ett nytt inlägg i din Teams-kanal:</p>
    
    <div style="background-color: #f0f8ff; border: 2px solid #0078d4; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">{short_description}</pre>
    </div>
    
    <p><strong>Så här gör du:</strong></p>
    <ol>
        <li>Kopiera texten i den blå rutan ovan</li>
        <li>Öppna Teams och gå till din AI-kanal</li>
        <li>Klistra in som ett nytt inlägg</li>
        <li>Klart! Teamet ser att det finns en ny sammanfattning</li>
    </ol>
    
    <p><em>Den fullständiga sammanfattningen ska kopieras till Teams-fliken (från det andra mailet).</em></p>
</body>
</html>
"""
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            # Skapa raw message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Skicka via Gmail API
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✓ Teams-inlägg skickat till {to_email} via Gmail API")
            
        except Exception as e:
            print(f"Fel vid emailsändning: {e}")
            raise
