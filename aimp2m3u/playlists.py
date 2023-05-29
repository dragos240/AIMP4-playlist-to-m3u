from typing import Any, Dict, List, Optional
from pathlib import Path
import os


class PlaylistSong:
    """Represents an individual song within a playlist

    Attributes:
        path: Path to the song
        song_name: Name of the song
        artist: Artist of the song
        album: Album of the song
    """
    path: str
    song_name: str
    artist: str
    album: str

    def __init__(self,
                 path: str,
                 song_name: str,
                 artist: str,
                 album: str):
        self.path = path
        self.song_name = song_name
        self.artist = artist
        self.album = album


class M3uPlaylist:
    """Represents an m3u playlist

    Attributes:
        filename: Filename of the playlist
        songs: All `PlaylistSong`s in the playlist
        common_path: Common path amongst all song paths
    """
    filename: str
    songs: List[PlaylistSong]
    common_path: str

    def __init__(self, name: str, songs: List[PlaylistSong]):
        self.filename = name + ".m3u"
        self.songs = songs

    def __str__(self) -> str:
        paths = [song.path for song in self.songs]

        return "\n".join(paths)

    def find_common_path(self) -> str:
        """Finds the base path common amongst all song paths

        Returns:
            str: The resulting common path
        """
        # Common parts between all paths
        common_paths = []
        song_paths = [Path(song.path) for song in self.songs]
        # Minimum number of parts (max possible common length)
        min_parts = min([len(song_path.parts) for song_path in song_paths])

        for i in range(min_parts):
            # Same part as last iteration?
            same_part = True
            # The last common part found
            last_part = None
            # Cycle through song paths
            for song_path in song_paths:
                part = song_path.parts[i]
                if last_part is not None \
                        and part != last_part:
                    same_part = False
                    break
                last_part = part
            if same_part:
                common_paths.append(last_part)
            last_part = None

        # Needs "\\" for later substitution
        return os.path.join(*common_paths) + "\\"

    def convert_to_relative(self):
        """
        Converts internal song paths to relative paths
        """
        self.common_path = self.find_common_path()

        for song in self.songs:
            song_path = song.path.replace("..\\", "")
            song_path = song_path.replace(self.common_path, "")
            song.path = song_path

    def paths_to_posix(self):
        """
        Convert song paths to POSIX format if in Windows format
        """
        for song in self.songs:
            song.path = song.path.replace("\\", '/')

    def sanitize_paths(self):
        self.convert_to_relative()
        self.paths_to_posix()
