"""
Google OAuth Setup Script
Kör detta lokalt första gången för att få refresh token
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive.file'
]

def setup_google_credentials():
    """
    Setup Google OAuth credentials
    1. Ladda ner OAuth client credentials från Google Cloud Console
    2. Spara som credentials.json i samma mapp som detta script
    3. Kör detta script
    4. Kopiera outputen till Railway environment variables
    """
    
    if not os.path.exists('credentials.json'):
        print("❌ Kan inte hitta credentials.json")
        print("📥 Ladda ner OAuth 2.0 Client ID från Google Cloud Console")
        print("💾 Spara som credentials.json i projektmappen")
        return
    
    print("🔐 Startar OAuth-flöde...")
    print("🌐 Din webbläsare öppnas snart för att godkänna åtkomst")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        SCOPES
    )
    
    creds = flow.run_local_server(port=0)
    
    # Skapa credentials dict för Railway
    credentials_dict = {
        'refresh_token': creds.refresh_token,
        'token': creds.token,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'token_uri': creds.token_uri,
        'scopes': creds.scopes
    }
    
    print("\n" + "="*60)
    print("✅ OAuth setup klart!")
    print("="*60)
    print("\n📋 Kopiera detta till Railway environment variable GMAIL_CREDENTIALS:")
    print("\n" + "="*60)
    print(json.dumps(credentials_dict, indent=2))
    print("="*60)
    
    # Spara också till fil för backup
    with open('google_credentials_backup.json', 'w') as f:
        json.dump(credentials_dict, f, indent=2)
    
    print("\n💾 Sparad till google_credentials_backup.json (ta bort efter copy!)")
    print("\n⚠️  VIKTIGT: Lägg INTE google_credentials_backup.json i Git!")

if __name__ == '__main__':
    setup_google_credentials()
