"""
Flask Web App - GUI för YouTube-hantering och manuell trigger
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import subprocess
import threading
from datetime import datetime
from services.supabase_service import SupabaseService

app = Flask(__name__)
supabase = SupabaseService()

# Global status för körning
run_status = {
    'running': False,
    'last_run': None,
    'last_result': None,
    'error': None
}

@app.route('/')
def index():
    """Dashboard"""
    summaries = supabase.get_all_summaries(limit=10)
    return render_template('index.html', summaries=summaries, status=run_status)

@app.route('/youtube')
def youtube():
    """YouTube-hantering"""
    videos = supabase.client.table('youtube_videos').select('*').order('created_at', desc=True).execute()
    return render_template('youtube.html', videos=videos.data)

@app.route('/api/youtube', methods=['POST'])
def add_youtube():
    """Lägg till ny YouTube-video"""
    data = request.json
    try:
        result = supabase.client.table('youtube_videos').insert({
            'title': data['title'],
            'url': data['url'],
            'category': data.get('category', ''),
            'type': data.get('type', ''),
            'description': data.get('description', ''),
            'is_active': True
        }).execute()
        return jsonify({'success': True, 'data': result.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/youtube/<int:video_id>', methods=['PUT'])
def update_youtube(video_id):
    """Uppdatera YouTube-video"""
    data = request.json
    try:
        result = supabase.client.table('youtube_videos').update(data).eq('id', video_id).execute()
        return jsonify({'success': True, 'data': result.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/youtube/<int:video_id>', methods=['DELETE'])
def delete_youtube(video_id):
    """Ta bort YouTube-video"""
    try:
        supabase.client.table('youtube_videos').delete().eq('id', video_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/youtube/<int:video_id>/toggle', methods=['POST'])
def toggle_youtube(video_id):
    """Aktivera/inaktivera YouTube-video"""
    try:
        video = supabase.client.table('youtube_videos').select('is_active').eq('id', video_id).execute()
        new_status = not video.data[0]['is_active']
        result = supabase.client.table('youtube_videos').update({'is_active': new_status}).eq('id', video_id).execute()
        return jsonify({'success': True, 'is_active': new_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/run', methods=['POST'])
def run_summary():
    """Kör sammanfattning manuellt"""
    global run_status
    
    if run_status['running']:
        return jsonify({'success': False, 'error': 'Körning pågår redan'}), 400
    
    def run_main():
        global run_status
        run_status['running'] = True
        run_status['last_run'] = datetime.now().isoformat()
        run_status['error'] = None
        
        try:
            result = subprocess.run(
                ['python', 'main.py'],
                capture_output=True,
                text=True,
                timeout=600  # 10 min timeout
            )
            
            run_status['running'] = False
            if result.returncode == 0:
                run_status['last_result'] = 'success'
            else:
                run_status['last_result'] = 'error'
                run_status['error'] = result.stderr
        except Exception as e:
            run_status['running'] = False
            run_status['last_result'] = 'error'
            run_status['error'] = str(e)
    
    thread = threading.Thread(target=run_main)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Körning startad'})

@app.route('/api/status')
def get_status():
    """Hämta körningsstatus"""
    return jsonify(run_status)

@app.route('/summary/<week>')
def view_summary(week):
    """Visa specifik sammanfattning"""
    summary = supabase.get_summary_by_week(week)
    if not summary:
        return "Sammanfattning hittades inte", 404
    return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
