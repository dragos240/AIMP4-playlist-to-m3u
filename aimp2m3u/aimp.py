from typing import Any, Dict, List, Optional
from pathlib import Path
import os

from .playlists import PlaylistSong, M3uPlaylist


class AimpPlaylist:
    """Represents an AIMP4 playlist

    Attributes:
        summary: Metadata info
        songs: List of `PlaylistSong`s in the playlist
    """
    summary: Dict[str, Any]
    songs: List[PlaylistSong]

    def __init__(self, summary, songs):
        self.summary = summary
        self.songs = songs

    @staticmethod
    def find_song_path(search_path: str,
                       filename: str) -> Path:
        """Finds the song within the specified search path

        Args:
            search_path (str): The search path to use
            filename (str): Name of the file to find

        Raises:
            FileNotFoundError: If the file can't be found
        """
        for dirpath, _, filenames in os.walk(search_path):
            for _filename in filenames:
                if filename == _filename:
                    finalpath = Path(dirpath)
                    finalpath = finalpath.joinpath(filename)

                    return finalpath

        raise FileNotFoundError()

    @classmethod
    def from_lines(cls, lines: List[str]) -> 'AimpPlaylist':
        """Create a new AimpPlaylist from of List of str

        Args:
            lines (List[str]): The lines to create a playlist from

        Returns:
            AimpPlaylist: The resulting AimpPlaylist
        """
        summary = {}
        songs = []
        current_root_path: Optional[str] = None
        section = None
        for line in lines:
            if "SUMMARY" in line:
                section = "summary"
                continue
            elif "CONTENT" in line:
                section = "content"
                continue
            if section is not None:
                if section == "summary":
                    try:
                        key, value = line.split("=")
                    except ValueError:
                        continue
                    summary[key] = value
                elif section == "content":
                    if line.startswith("-"):
                        # This marks a new section with a base path
                        current_root_path = line[1:]
                        continue
                    line_parts = line.split("|")
                    line_path = Path(line_parts[0])
                    (song_name,
                        artist,
                        album) = line_parts[1:4]

                    file_path = cls.find_song_path(current_root_path,
                                                   line_path.name)

                    song = PlaylistSong(
                        str(file_path), song_name, artist, album)
                    songs.append(song)

        return cls(summary, songs)

    @classmethod
    def from_filename(cls, filename: str) -> 'AimpPlaylist':
        lines = []
        try:
            with open(filename, "r", encoding="utf-16") as f:
                lines = f.read().splitlines()
        except FileNotFoundError as e:
            print("Playlist file doesn't exist")
            raise e

        return cls.from_lines(lines)

    def to_m3u(self) -> M3uPlaylist:
        return M3uPlaylist(self.summary["Name"], self.songs)
