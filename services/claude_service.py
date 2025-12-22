"""Claude AI Service - Analyserar och sammanfattar veckan"""

import os
from anthropic import Anthropic

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_week(self, newsletters, youtube_videos):
        """Analysera veckan och generera Markdown-sammanfattning"""
        
        # Bygg prompt med all data
        prompt = self._build_analysis_prompt(newsletters, youtube_videos)
        
        # Anropa Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        markdown_content = response.content[0].text
        
        # Extrahera YouTube-picks från resultatet (för databas)
        youtube_picks = self._extract_youtube_picks(markdown_content)
        
        return {
            'markdown': markdown_content,
            'youtube_picks': youtube_picks
        }
    
    def _build_analysis_prompt(self, newsletters, youtube_videos):
        """Bygg prompt för Claude"""
        
        # Skapa sammanfattning av newsletters (begränsa längd)
        newsletters_summary = ""
        for i, nl in enumerate(newsletters[:30], 1):  # Max 30 newsletters
            # Använd snippet istället för full HTML för att spara tokens
            newsletters_summary += f"\n## Newsletter {i}\n"
            newsletters_summary += f"**Från:** {nl['from']}\n"
            newsletters_summary += f"**Ämne:** {nl['subject']}\n"
            newsletters_summary += f"**Drive-länk:** {nl['drive_url']}\n"
            newsletters_summary += f"**Innehåll (kort):** {nl['snippet'][:300]}...\n"
        
        # Skapa lista av YouTube-videos
        youtube_summary = ""
        for i, video in enumerate(youtube_videos, 1):
            youtube_summary += f"\n{i}. **{video['title']}**\n"
            youtube_summary += f"   - URL: {video['url']}\n"
            youtube_summary += f"   - Kategori: {video['category']}\n"
            youtube_summary += f"   - Typ: {video['type']}\n"
            youtube_summary += f"   - Beskrivning: {video['description']}\n"
        
        prompt = f"""Du är en AI-expert som skapar engagerande veckosammanfattningar om AI för arbetskollegor.

Din uppgift är att analysera dessa newsletters och YouTube-videos och skapa en veckosammanfattning i Markdown-format som ska postas på Teams.

# NEWSLETTERS FRÅN VECKAN
{newsletters_summary}

# TILLGÄNGLIGA YOUTUBE-VIDEOS
{youtube_summary}

# SKAPA FÖLJANDE SAMMANFATTNING I MARKDOWN

Skapa ett Teams-inlägg med denna struktur:

---
# 🤖 AI-veckans sammanfattning

## ⚡ Veckans highlights
[De 3 mest intressanta sakerna som hänt denna vecka - kort och kärnfullt]

## 📰 Top 3 Nyhetsbrev
[Välj de 3 mest intressanta/relevanta newslettersna. För varje:]
**[Titel]** - [2-3 meningar sammanfattning]
🔗 [Länk till Drive]

## 🎥 Top 3 YouTube-klipp
[Välj 3 videos från listan som passar bäst till veckans tema. För varje:]
**[Titel]** - [1-2 meningar varför den är intressant]
🔗 [URL]

## 😄 Lättsamt & Underhållande
[Välj 1-2 newsletters eller videos som är mer underhållande/lättare]
🔗 [Länkar]

## 💡 AI-tips i veckan
[Ett konkret tips som kollegor kan testa direkt denna vecka - koppla till något från newslettersna]

## 🎯 Så kan VI använda detta
[2-3 konkreta exempel på hur er organisation/team kan använda något från veckans nyheter]

## 🏆 AI-utmaning för veckan (valfritt)
[En liten utmaning/uppgift för nyfikna kollegor att testa]

---

**Viktiga riktlinjer:**
- Skriv på svenska
- Använd emojis sparsamt men strategiskt
- Håll det kortfattat och engagerande
- **TON: Avslappnad, entusiastisk och lättläst - som en kollega som tipsar över en kopp kaffe**
- **Undvik corporate-speak och formella formuleringar**
- **Skriv som att du pratar med en vän, inte en konferens**
- Fokusera på praktisk nytta
- Länka alltid till originalinnehåll
- Gör det lätt att scanna (tydliga rubriker)
- Total längd: max 2 skärmlängder på mobil

Skapa sammanfattningen nu:"""

        return prompt
    
    def _extract_youtube_picks(self, markdown):
        """Extrahera valda YouTube-videos från Markdown (förenklad)"""
        # Förenklad extraktion - returnera tom lista
        # Kan förbättras senare om vi behöver spara detta strukturerat
        return []
