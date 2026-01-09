"""Claude AI Service - Analyserar och sammanfattar veckan"""

import os
import random
from datetime import datetime, timedelta
from anthropic import Anthropic

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def _calculate_video_weight(self, published_date):
        """Beräkna sannolikhet baserat på ålder"""
        if not published_date:
            return 0.3  # Default medel-sannolikhet om datum saknas
        
        try:
            if isinstance(published_date, str):
                pub_date = datetime.strptime(published_date, '%Y-%m-%d').date()
            else:
                pub_date = published_date
            
            today = datetime.now().date()
            days_old = (today - pub_date).days
            
            # Viktning baserat på ålder
            if days_old < 30:  # <1 månad
                return 0.8
            elif days_old < 90:  # 1-3 månader
                return 0.5
            elif days_old < 180:  # 3-6 månader
                return 0.3
            else:  # >6 månader
                return 0.1
        except:
            return 0.3
    
    def _weighted_video_selection(self, videos, count=3):
        """Välj videos med viktad slumpmässighet"""
        if not videos:
            return []
        
        # Beräkna vikter för alla videos
        weighted_videos = []
        for video in videos:
            weight = self._calculate_video_weight(video.get('published_date'))
            weighted_videos.append((video, weight))
        
        # Slumpmässigt urval baserat på vikter
        selected = []
        remaining = weighted_videos.copy()
        
        for _ in range(min(count, len(videos))):
            if not remaining:
                break
            
            # Weighted random choice
            total_weight = sum(w for _, w in remaining)
            if total_weight == 0:
                # Fallback om alla har vikt 0
                video, _ = random.choice(remaining)
            else:
                rand = random.uniform(0, total_weight)
                cumsum = 0
                video = None
                for v, w in remaining:
                    cumsum += w
                    if rand <= cumsum:
                        video = v
                        break
                
                if video is None:
                    video = remaining[0][0]
            
            selected.append(video)
            remaining = [(v, w) for v, w in remaining if v != video]
        
        return selected
    
    def analyze_week(self, newsletters, youtube_videos, week_number):
        """Analysera veckan och generera Markdown-sammanfattning + kort beskrivning"""
        
        # Gör viktad urval av YouTube-videos
        selected_videos = self._weighted_video_selection(youtube_videos, count=10)
        
        # Bygg prompt med all data
        prompt = self._build_analysis_prompt(newsletters, selected_videos, week_number)
        
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
        
        # Generera kort beskrivning för Teams-inlägg
        short_description = self._generate_short_description(newsletters, selected_videos, week_number)
        
        # Extrahera YouTube-picks från resultatet (för databas)
        youtube_picks = self._extract_youtube_picks(markdown_content)
        
        return {
            'markdown': markdown_content,
            'short_description': short_description,
            'youtube_picks': youtube_picks
        }
    
    def _generate_short_description(self, newsletters, videos, week_number):
        """Generera kort beskrivning för Teams-inlägg"""
        
        # Ta top ämnen från newsletters
        topics_prompt = f"""Baserat på dessa newsletters, skapa en kort punktlista med 4-5 nyckelhändelser denna vecka.

NEWSLETTERS (ämnesrader):
{chr(10).join([f"- {nl['subject']}" for nl in newsletters[:15]])}

Skapa ENDAST en bullet-lista med 4-5 korta punkter (max 8 ord per punkt). Format:
• Punkt 1
• Punkt 2
• Punkt 3
etc.

VIKTIGT: Bara bullets, ingen annan text."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            temperature=0.5,
            messages=[{"role": "user", "content": topics_prompt}]
        )
        
        bullets = response.content[0].text.strip()
        
        # Bygg kort meddelande
        short_msg = f"""🤖 AI-veckans sammanfattning är uppdaterad (Vecka {week_number})

Den här veckan:
{bullets}

⏱️ Lästid: ~5–6 min  
👉 Full sammanfattning finns i fliken ovan"""
        
        return short_msg
    
    def _build_analysis_prompt(self, newsletters, youtube_videos, week_number):
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
# 🤖 AI-veckans sammanfattning - Vecka {week_number}

## ⚡ Veckans highlights
[De 3 mest intressanta sakerna som hänt denna vecka - kort och kärnfullt]

## 📰 Top 3 Nyhetsbrev
[Välj de 3 mest intressanta/relevanta newslettersna. För varje:]
**[Titel]** - [2-3 meningar sammanfattning]
🔗 [Länk till Drive]

## 🎥 Top 3 YouTube-klipp
[Välj 3 videos från listan som passar bäst till veckans tema. För varje:]
**[Titel]** - [1-2 meningar varför den är intressant]
🔗 [Klicka här för video](URL)

VIKTIGT: Använd Markdown-format för länkar: [Länktext](URL), inte bara URL:en.

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
