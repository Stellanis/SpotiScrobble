import { createContext, useContext, useState, useRef, useEffect } from 'react';

const PlayerContext = createContext();

export function PlayerProvider({ children }) {
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [volume, setVolume] = useState(1); // 0.0 to 1.0
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isReady, setIsReady] = useState(false);
    const [activeDownloads, setActiveDownloads] = useState([]);

    const audioRef = useRef(new Audio());

    // Poll for active downloads
    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await fetch('/api/jobs');
                if (res.ok) {
                    const data = await res.json();
                    setActiveDownloads(data.active_downloads || []);
                }
            } catch (e) {
                console.error("Failed to fetch jobs:", e);
            }
        };

        const interval = setInterval(fetchJobs, 2000);
        fetchJobs(); // Initial fetch

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const audio = audioRef.current;

        const handleTimeUpdate = () => setProgress(audio.currentTime);
        const handleDurationChange = () => setDuration(audio.duration);
        const handleEnded = () => {
            setIsPlaying(false);
            setProgress(0);
        };
        const handleCanPlay = () => setIsReady(true);

        audio.addEventListener('timeupdate', handleTimeUpdate);
        audio.addEventListener('durationchange', handleDurationChange);
        audio.addEventListener('ended', handleEnded);
        audio.addEventListener('canplay', handleCanPlay);

        return () => {
            audio.removeEventListener('timeupdate', handleTimeUpdate);
            audio.removeEventListener('durationchange', handleDurationChange);
            audio.removeEventListener('ended', handleEnded);
            audio.removeEventListener('canplay', handleCanPlay);
        };
    }, []);

    const playTrack = (track) => {
        const audio = audioRef.current;

        // Use the backend-provided URL if available, fallback to constructed one
        // The backend should now be returning 'audio_url' for downloaded tracks
        let url = track.audio_url;

        if (!url) {
            console.warn("No audio_url found for track:", track);
            // Fallback: This likely won't work due to the folder structure issue we just fixed, 
            // but keeps the old logic as a last resort.
            const filename = encodeURIComponent(`${track.artist} - ${track.title}.mp3`);
            url = `/api/audio/${filename}`;
        }

        // Check if we are already playing this track (by URL match)
        // audio.src is the full absolute URL, so we check if it ends with our relative URL or just check title
        const isSameTrack = currentTrack?.title === track.title;

        if (isSameTrack && !audio.paused) {
            return; // Already playing
        }

        if (!isSameTrack) {
            console.log("Loading URL:", url);
            audio.src = url;
            audio.load();
            setCurrentTrack(track);
            setIsReady(false);
        }

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise
                .then(() => setIsPlaying(true))
                .catch(e => {
                    console.error("Playback failed:", e);
                    setIsPlaying(false);
                    // If 404, it might be the fallback failing or the URL being wrong
                });
        }
    };

    const togglePlay = () => {
        if (!currentTrack) return;

        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const seek = (time) => {
        audioRef.current.currentTime = time;
        setProgress(time);
    };

    const updateVolume = (val) => {
        setVolume(val);
        audioRef.current.volume = val;
    };

    return (
        <PlayerContext.Provider value={{
            currentTrack,
            isPlaying,
            volume,
            progress,
            duration,
            isReady,
            playTrack,
            togglePlay,
            seek,
            updateVolume,
            activeDownloads
        }}>
            {children}
        </PlayerContext.Provider>
    );
}

export function usePlayer() {
    return useContext(PlayerContext);
}
