import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Music, Disc, Search, CheckCircle, Loader2 } from 'lucide-react';
import { cn } from './utils';

const API_URL = 'http://localhost:8000';

function App() {
  const [username, setUsername] = useState('wife5711'); // Default from user request
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState({});

  const fetchScrobbles = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/scrobbles/${username}`);
      setTracks(response.data);
    } catch (error) {
      console.error("Error fetching scrobbles:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (track) => {
    const query = `${track.artist} - ${track.title}`;
    setDownloading(prev => ({ ...prev, [query]: 'loading' }));
    try {
      await axios.post(`${API_URL}/download`, {
        query,
        artist: track.artist,
        title: track.title,
        album: track.album
      });
      setDownloading(prev => ({ ...prev, [query]: 'success' }));
    } catch (error) {
      console.error("Error downloading:", error);
      setDownloading(prev => ({ ...prev, [query]: 'error' }));
    }
  };

  useEffect(() => {
    fetchScrobbles();
  }, []);

  return (
    <div className="min-h-screen bg-spotify-black text-white p-8">
      <div className="max-w-4xl mx-auto space-y-8">

        {/* Header */}
        <header className="flex items-center justify-between glass-panel p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-spotify-green rounded-full">
              <Music className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Spotify Downloader</h1>
              <p className="text-spotify-grey text-sm">Powered by Last.fm & yt-dlp</p>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-spotify-dark/50 p-2 rounded-lg border border-white/5">
            <Search className="w-5 h-5 text-spotify-grey" />
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchScrobbles()}
              className="bg-transparent border-none outline-none text-sm w-32 placeholder:text-spotify-grey"
              placeholder="Last.fm User"
            />
            <button
              onClick={fetchScrobbles}
              className="bg-spotify-green hover:bg-green-500 text-white px-4 py-1.5 rounded-md text-sm font-medium transition-colors"
            >
              Fetch
            </button>
          </div>
        </header>

        {/* Track List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Disc className="w-5 h-5 text-spotify-green" />
            Recent Scrobbles
          </h2>

          {loading ? (
            <div className="flex justify-center py-20">
              <Loader2 className="w-10 h-10 animate-spin text-spotify-green" />
            </div>
          ) : (
            <div className="grid gap-4">
              <AnimatePresence>
                {tracks.map((track, index) => {
                  const query = `${track.artist} - ${track.title}`;
                  const status = downloading[query];

                  return (
                    <motion.div
                      key={`${track.timestamp}-${index}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ delay: index * 0.05 }}
                      className="glass-panel p-4 flex items-center justify-between group hover:bg-white/10 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-md overflow-hidden bg-spotify-dark relative">
                          {track.image ? (
                            <img src={track.image} alt={track.title} className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-spotify-grey">
                              <Music className="w-8 h-8" />
                            </div>
                          )}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{track.title}</h3>
                          <p className="text-spotify-grey">{track.artist}</p>
                          <p className="text-xs text-spotify-grey/60 mt-1">{track.album}</p>
                        </div>
                      </div>

                      <button
                        onClick={() => handleDownload(track)}
                        disabled={status === 'loading' || status === 'success'}
                        className={cn(
                          "p-3 rounded-full transition-all duration-300",
                          status === 'success' ? "bg-spotify-green text-white" :
                            status === 'loading' ? "bg-spotify-grey/20 text-spotify-green" :
                              "bg-white/10 text-white hover:bg-spotify-green hover:scale-110"
                        )}
                      >
                        {status === 'success' ? (
                          <CheckCircle className="w-6 h-6" />
                        ) : status === 'loading' ? (
                          <Loader2 className="w-6 h-6 animate-spin" />
                        ) : (
                          <Download className="w-6 h-6" />
                        )}
                      </button>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
