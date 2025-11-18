1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Stellanis/Spotify_scrobbler.git
    cd Spotify_scrobbler
    ```

2.  **Configure Environment**:
    Create a `.env` file in `backend/` (or set via Docker env vars):
    ```env
    LASTFM_API_KEY=your_api_key_here
    LASTFM_USER=your_username
    ```

3.  **Run**:
    ```bash
    docker-compose up --build -d
    ```

4.  **Access**:
    -   Frontend: `http://localhost:3001`
    -   Backend: `http://localhost:8000`

    volumes:
      - /volume1/docker/data/Music:/app/downloads
    ```
7.  **Deploy Stack**.

## 📂 Folder Structure

Downloaded music is organized automatically:

```
/downloads
├── Artist Name
│   └── Album Name
│       └── Song Title.mp3
└── Another Artist
    └── Album Name
        └── Song Title.mp3
```

## 🔧 Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LASTFM_API_KEY` | **Required**. Get one at [last.fm/api](https://www.last.fm/api) | - |
| `LASTFM_USER` | **Required**. The user to fetch scrobbles for. | - |
| `LASTFM_API_SECRET` | Optional. Not currently used for public reads. | - |

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)