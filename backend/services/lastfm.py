import pylast
import os
import time

from database import get_setting

class LastFMService:
    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.network = None
        self._cache = {}
        self._cache_ttl = 120  # 2 minutes

    def get_recent_tracks(self, user: str, limit: int = 10):
        # Check cache
        cache_key = f"{user}_{limit}"
        now = time.time()
        
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if now - timestamp < self._cache_ttl:
                return data

        # Refresh credentials from DB in case they changed
        self.api_key = get_setting("LASTFM_API_KEY") or os.getenv("LASTFM_API_KEY")
        
        if not self.api_key:
            print("Last.fm API key not configured")
            return []
        
        try:
            import requests
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                "method": "user.getrecenttracks",
                "user": user,
                "api_key": self.api_key,
                "format": "json",
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            tracks = []
            if "recenttracks" in data and "track" in data["recenttracks"]:
                raw_tracks = data["recenttracks"]["track"]
                if isinstance(raw_tracks, dict):
                    raw_tracks = [raw_tracks]
                    
                for track in raw_tracks:
                    # Extract image
                    image_url = None
                    images = track.get("image", [])
                    if isinstance(images, list):
                        # Try to find extralarge, then large, then whatever is last
                        for img in images:
                            if img.get("size") == "extralarge":
                                image_url = img.get("#text")
                                break
                        if not image_url and images:
                             image_url = images[-1].get("#text")
                    
                    # Extract artist name
                    artist_obj = track.get("artist")
                    artist = artist_obj.get("#text") if isinstance(artist_obj, dict) else artist_obj
                    
                    # Extract album name
                    album_obj = track.get("album")
                    album = album_obj.get("#text") if isinstance(album_obj, dict) else album_obj
                    
                    # Timestamp
                    timestamp = None
                    if "date" in track:
                        timestamp = track["date"].get("uts")
                    
                    # Filter out empty artist/title if any
                    if artist and track.get("name"):
                        tracks.append({
                            "artist": artist,
                            "title": track.get("name"),
                            "album": album,
                            "image": image_url,
                            "timestamp": timestamp
                        })
            
            # Update cache
            self._cache[cache_key] = (now, tracks)
            return tracks
            
        except Exception as e:
            print(f"Error fetching from Last.fm: {e}")
            # If we have stale data, return it instead of crashing
            if cache_key in self._cache:
                return self._cache[cache_key][1]
            return []
