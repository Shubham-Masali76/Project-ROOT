import pyautogui
import pyperclip
import time
import re
import ollama
import os
from youtube_transcript_api import YouTubeTranscriptApi

LOCAL_MODEL = "llama3.2:1b"

def steal_url():
    """Uses the ghost hand to copy the URL from the active browser."""
    # Press Ctrl+L to focus URL bar
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.2)
    # Press Ctrl+C to copy
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)
    # Press Escape to defocus the URL bar
    pyautogui.press('esc')
    time.sleep(0.2)
    return pyperclip.paste()

def extract_video_id(url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if match:
        return match.group(1)
    return None

def fetch_transcript(video_id):
    """Downloads the actual subtitles of the video to understand it."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript])
        # Keep it short so the local LLM doesn't take 5 minutes to read it
        return text[:3000]
    except Exception:
        return None

def generate_comment(transcript):
    """Uses the local Brain to formulate a comment based on what it watched."""
    prompt = f"Based on this YouTube video transcript, write a short, fun, 1-sentence YouTube comment. Do not use hashtags or quotes. Transcript: {transcript}"
    try:
        response = ollama.chat(model=LOCAL_MODEL, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].replace('"', '').strip()
    except Exception:
        return "Great video, thanks for sharing!"

def execute(command_text):
    print("[Ghost Protocol] Initiated. Stealing URL...")
    
    url = steal_url()
    if "youtube.com" not in url and "youtu.be" not in url:
        return "I could not find a YouTube video on your active screen. Please make sure the video is open."
        
    video_id = extract_video_id(url)
    if not video_id:
        return "I could not extract the video ID."
        
    print("[Ghost Protocol] Downloading transcript...")
    transcript = fetch_transcript(video_id)
    if not transcript:
        return "I could not read the subtitles for this video, so I can't generate a specific comment."
        
    print("[Ghost Protocol] Thinking of a smart comment...")
    comment = generate_comment(transcript)
    
    # Save the comment to clipboard so the user can easily paste it
    pyperclip.copy(comment)
    
    # ---------------------------------------------------------
    # GHOST HAND EXECUTION (Physical Liking & Commenting)
    # ---------------------------------------------------------
    
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    like_btn = os.path.join(assets_dir, 'like.png')
    comment_box = os.path.join(assets_dir, 'comment.png')
    
    # Scroll down to make the comment box visible
    pyautogui.scroll(-800)
    time.sleep(1)
    
    # Try to find and click the like button if the image exists
    clicked_like = False
    if os.path.exists(like_btn):
        try:
            btn = pyautogui.locateCenterOnScreen(like_btn, confidence=0.8)
            if btn:
                pyautogui.click(btn)
                time.sleep(0.5)
                clicked_like = True
        except Exception:
            pass
            
    # Try to find and click the comment box if the image exists
    clicked_comment = False
    if os.path.exists(comment_box):
        try:
            box = pyautogui.locateCenterOnScreen(comment_box, confidence=0.8)
            if box:
                pyautogui.click(box)
                time.sleep(0.5)
                # Type the comment like a human!
                pyautogui.write(comment, interval=0.03)
                time.sleep(0.5)
                clicked_comment = True
        except Exception:
            pass
            
    if clicked_comment:
        return "Ghost protocol complete. I watched the video, dropped a like, and typed the comment for you."
    else:
        return "I watched the video and generated a comment. I copied it to your clipboard. Just press Ctrl V to paste it."
