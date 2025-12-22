-- Supabase Database Schema
-- Kör detta i Supabase SQL Editor

-- Tabell för veckosammanfattningar
CREATE TABLE IF NOT EXISTS weekly_summaries (
    id BIGSERIAL PRIMARY KEY,
    week TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    markdown_content TEXT NOT NULL,
    status TEXT DEFAULT 'completed',
    newsletter_count INTEGER DEFAULT 0
);

-- Tabell för individuella newsletters
CREATE TABLE IF NOT EXISTS newsletters (
    id BIGSERIAL PRIMARY KEY,
    summary_id BIGINT REFERENCES weekly_summaries(id) ON DELETE CASCADE,
    week TEXT NOT NULL,
    title TEXT NOT NULL,
    from_email TEXT,
    date TEXT,
    drive_url TEXT NOT NULL,
    snippet TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index för snabbare queries
CREATE INDEX IF NOT EXISTS idx_newsletters_week ON newsletters(week);
CREATE INDEX IF NOT EXISTS idx_newsletters_summary_id ON newsletters(summary_id);
CREATE INDEX IF NOT EXISTS idx_weekly_summaries_created_at ON weekly_summaries(created_at DESC);

-- Row Level Security (RLS) - aktivera om du vill
-- ALTER TABLE weekly_summaries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;

-- Tabell för YouTube-videos
CREATE TABLE IF NOT EXISTS youtube_videos (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    category TEXT,
    type TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index för YouTube-videos
CREATE INDEX IF NOT EXISTS idx_youtube_videos_active ON youtube_videos(is_active);
CREATE INDEX IF NOT EXISTS idx_youtube_videos_category ON youtube_videos(category);

-- Tabell för YouTube-videos
CREATE TABLE IF NOT EXISTS youtube_videos (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    category TEXT,
    type TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index för YouTube-videos
CREATE INDEX IF NOT EXISTS idx_youtube_videos_active ON youtube_videos(is_active);
CREATE INDEX IF NOT EXISTS idx_youtube_videos_category ON youtube_videos(category);

-- Policies (exempel - anpassa efter behov)
-- CREATE POLICY "Enable read access for all users" ON weekly_summaries FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON newsletters FOR SELECT USING (true);
-- CREATE POLICY "Enable all for youtube_videos" ON youtube_videos FOR ALL USING (true);
