# 🤖 AI Newsletter Weekly Summary

Automatisk veckosammanfattning av AI-newsletters med web-GUI för hantering.

## ✨ Features

- 🤖 **AI-analys** med Claude av newsletters
- 📅 **Auto-körning** varje fredag kl 08:00
- 🎛️ **Web-GUI** för hantering och manuell trigger
- 🎥 **YouTube-databas** i Supabase
- 📧 **Email-notifikationer** med färdigt Markdown
- 📊 **Historik** av alla sammanfattningar
- ✅ **Auto-markering** av lästa newsletters

## 🎯 Vad gör den?

1. Hämtar **olästa** newsletters från Gmail (label: "Newsletters")
2. Från förra fredagen 08:00 till denna fredagen 08:00
3. Sparar HTML-kopior på Google Drive
4. Hämtar YouTube-videos från Supabase
5. AI-analys med Claude
6. Genererar Markdown-sammanfattning
7. Skickar email med färdigt innehåll
8. Markerar newsletters som lästa
9. Copy-paste till Teams!

## 🛠️ Setup

### 1. Supabase Setup

1. Skapa nytt projekt på [supabase.com](https://supabase.com)
2. Gå till SQL Editor
3. Kör innehållet från `supabase_schema.sql`
4. Spara URL och anon key

### 2. Google Cloud Setup

#### Gmail & Drive API
1. Gå till [Google Cloud Console](https://console.cloud.google.com)
2. Skapa nytt projekt
3. Aktivera APIs:
   - Gmail API
   - Google Drive API
4. Skapa OAuth 2.0 credentials:
   - Application type: Desktop app
   - Ladda ner JSON
5. Kör första gången lokalt för att få refresh token:
   ```bash
   python setup_google_auth.py
   ```
   Detta öppnar browser och ger dig en credentials JSON med refresh_token

**Scopes som behövs:**
- `gmail.modify` - Läsa och markera newsletters som lästa
- `gmail.send` - Skicka email via Gmail API
- `drive.file` - Spara newsletters till Drive

#### Google Drive Mapp
1. Skapa en mapp för newsletters på Drive
2. Kopiera mapp-ID från URL:
   `https://drive.google.com/drive/folders/DETTA_ÄR_FOLDER_ID`

### 3. Claude API

1. Gå till [console.anthropic.com](https://console.anthropic.com)
2. Skapa API key
3. Spara nyckeln

### 4. Migrera YouTube-data

1. Lägg din Excel-fil i projektmappen
2. Kör migration:
   ```bash
   export SUPABASE_URL=...
   export SUPABASE_KEY=...
   python migrate_youtube.py Videolänkar.xlsx
   ```

### 5. Railway Setup

1. Pusha kod till GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-repo-url
   git push -u origin main
   ```

2. Skapa projekt på [railway.app](https://railway.app)
3. Koppla GitHub repo
4. Lägg till Environment Variables i Railway dashboard:

   ```
   CLAUDE_API_KEY=sk-ant-xxx
   GMAIL_CREDENTIALS={"refresh_token":"xxx","client_id":"xxx"...}
   GOOGLE_DRIVE_FOLDER_ID=xxx
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=xxx
   EMAIL_TO=lars.newsletters19@gmail.com
   EMAIL_FROM=lars.newsletters19@gmail.com
   PORT=5000
   ```

5. Deploy!
6. Railway ger dig en URL (t.ex. `https://your-app.railway.app`)
7. Öppna URL:en för att komma åt GUI:t!

**OBS:** Gmail credentials behöver scopesen: `gmail.modify`, `gmail.send`, `drive.file`

### 6. Automatisk körning

Railway använder `Procfile` för både web och cron:
- **Web:** Flask-app på port 5000
- **Cron:** Körs varje fredag kl 08:00

**Cron-logik:** Samlar newsletters från förra fredagen 08:00 till denna fredagen 08:00.

## 🌐 Web-GUI

Railway ger dig en URL för GUI:t:

### Dashboard (`/`)
- ▶️ **Kör nu** - Manuell trigger
- 📊 **Status** - Senaste körning
- 📜 **Historik** - Alla sammanfattningar

### YouTube (`/youtube`)
- ➕ **Lägg till** videos
- ✏️ **Aktivera/inaktivera** videos
- 🗑️ **Ta bort** videos

### Sammanfattning (`/summary/<vecka>`)
- 👀 **Preview** av Markdown
- 📋 **Kopiera** till Teams

## 📁 Struktur

```
.
├── app.py                  # Flask web-app
├── main.py                 # Huvudflöde (cron-job)
├── services/
│   ├── gmail_service.py    # Hämta från Gmail + markera läst
│   ├── drive_service.py    # Spara till Drive
│   ├── youtube_service.py  # Hämta från Supabase
│   ├── claude_service.py   # AI-analys
│   ├── supabase_service.py # Databas
│   └── email_service.py    # Skicka resultat
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Dashboard
│   ├── youtube.html        # YouTube-hantering
│   └── summary.html        # Sammanfattning
├── utils/
│   └── logger.py           # Logging
├── requirements.txt        # Python packages
├── Procfile               # Railway (web + cron)
├── railway.json           # Railway config
├── nixpacks.toml          # Build config
├── supabase_schema.sql    # Databasschema
├── migrate_youtube.py     # YouTube Excel → Supabase
└── setup_google_auth.py   # OAuth setup
```

## 🚀 Lokal testning

```bash
# Installera dependencies
pip install -r requirements.txt

# Kopiera environment variables
cp .env.example .env
# Fyll i dina värden i .env

# Kör migration (första gången)
python migrate_youtube.py Videolänkar.xlsx

# Starta web-app
python app.py
# Öppna http://localhost:5000

# Eller kör cron manuellt
python main.py
```

## 📧 Output

Du får ett email med:
- Färdig Markdown-sammanfattning
- Instruktioner för Teams
- Kopiera → Klistra in → Klart!

## 🔧 Underhåll

### Uppdatera kod
```bash
git add .
git commit -m "Update"
git push
```
Railway deployer automatiskt!

### Ändra schema
Ändra cron i `railway.json`:
- Måndag 08:00: `0 8 * * 1`
- Varje dag 09:00: `0 9 * * *`

### Debugging
Kolla Railway logs i dashboard.

## 🎨 Anpassa

### Claude prompt
Redigera `services/claude_service.py` → `_build_analysis_prompt()`

### Email-template
Redigera `services/email_service.py` → `send_summary()`

### GUI styling
Redigera HTML-templates i `templates/`

### Cron-schema
Redigera `Procfile` - ändra `friday.at('08:00')` till önskat schema

## 💡 Tips

- Web-GUI = enkel hantering av videos
- Första körningen kan ta 2-3 min
- Gmail OAuth token refreshas automatiskt
- Supabase sparar historik (sök gamla veckor)
- Google Drive = delbar backup av newsletters
- Endast olästa newsletters bearbetas varje gång

## 🆘 Troubleshooting

**Fel: Gmail authentication**
→ Kör `setup_google_auth.py` lokalt igen

**Fel: Supabase connection**
→ Kolla att URL och key är rätt

**Fel: Email skickas inte**
→ Kolla Gmail app password

**Cron körs inte**
→ Kolla Railway logs, verifiera syntax i railway.json

## 📝 Licens

MIT - gör vad du vill!
