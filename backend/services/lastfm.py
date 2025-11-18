import pylast
import os

class LastFMService:
    def __init__(self):
        self.api_key = os.getenv("LASTFM_API_KEY")
        self.api_secret = os.getenv("LASTFM_API_SECRET")
        self.network = None
        if self.api_key:
            self.network = pylast.LastFMNetwork(api_key=self.api_key, api_secret=self.api_secret)

    def get_recent_tracks(self, user: str, limit: int = 10):
        if not self.network:
            raise ValueError("Last.fm credentials not configured")
        
        user_obj = self.network.get_user(user)
        recent_tracks = user_obj.get_recent_tracks(limit=limit)
        
        tracks = []
        for track in recent_tracks:
            image_url = None
            try:
                image_url = track.track.get_cover_image()
            except Exception:
                pass

            tracks.append({
                "artist": track.track.artist.name,
                "title": track.track.title,
                "album": track.album,
                "image": image_url,
                "timestamp": track.timestamp
            })
        return tracks
