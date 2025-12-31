#!/usr/bin/env python3
"""
POC: YouTube Transcript API Test
Video: https://youtu.be/55ox9fB3x-E
Updated for youtube-transcript-api v1.2.x (instance-based API)
"""

from youtube_transcript_api import YouTubeTranscriptApi
import json

VIDEO_ID = "55ox9fB3x-E"

def fetch_transcript(video_id):
    """Fetch transcript for a YouTube video."""
    try:
        print("=" * 60)
        print(f"Fetching transcript for video: {video_id}")
        print("=" * 60 + "\n")
        
        # v1.2.x: Create an instance first
        ytt_api = YouTubeTranscriptApi()
        
        # List available transcripts
        print("Listing available transcripts...")
        transcript_list = ytt_api.list(video_id)
        
        print("Available transcripts:")
        for transcript in transcript_list:
            print(f"  - {transcript.language} ({transcript.language_code})")
            print(f"    Generated: {transcript.is_generated}")
        
        print("\n" + "-" * 60)
        print("Fetching transcript...")
        
        # Fetch the transcript (prefer English)
        fetched = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
        
        # Convert to list and combine text
        transcript_data = list(fetched)
        full_text = " ".join([entry.text for entry in transcript_data])
        
        print("\nTRANSCRIPT PREVIEW (first 2000 chars):")
        print("-" * 60)
        print(full_text[:2000])
        print("-" * 60)
        
        print(f"\n✅ SUCCESS! Got {len(transcript_data)} segments, {len(full_text)} total characters")
        
        # Save full transcript to file
        output = {
            "video_id": video_id,
            "video_url": f"https://youtu.be/{video_id}",
            "total_segments": len(transcript_data),
            "total_characters": len(full_text),
            "full_text": full_text,
            "segments_sample": [
                {"text": s.text, "start": s.start, "duration": s.duration} 
                for s in transcript_data[:20]
            ]
        }
        
        with open("transcript_output.json", "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n📁 Full transcript saved to: transcript_output.json")
        
        return transcript_data
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print(f"Testing YouTube Transcript API on video: {VIDEO_ID}")
    print(f"URL: https://youtu.be/{VIDEO_ID}\n")
    fetch_transcript(VIDEO_ID)
