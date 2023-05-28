import argparse
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
    filename: str
    songs: List[PlaylistSong]

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

        return os.path.join(*common_paths)


class AimpPlaylist:
    summary: Dict[str, Any]
    songs: List[PlaylistSong]

    def __init__(self, summary, songs):
        self.summary = summary
        self.songs = songs

    @staticmethod
    def find_song_path(search_path: str,
                       filename: str) -> Path:
        for dirpath, _, filenames in os.walk(search_path):
            for _filename in filenames:
                if filename == _filename:
                    finalpath = Path(dirpath)
                    finalpath = finalpath.joinpath(filename)

                    return finalpath

        raise FileNotFoundError()

    @classmethod
    def from_lines(cls, lines: List[str]) -> 'AimpPlaylist':
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
                    # print(current_root_path, line_path.name)

                    song = PlaylistSong(
                        str(file_path), song_name, artist, album)
                    songs.append(song)

        return cls(summary, songs)

    def to_m3u(self) -> M3uPlaylist:
        return M3uPlaylist(self.summary["Name"], self.songs)


def parse_sections(file_data: str) -> M3uPlaylist:
    lines = file_data.splitlines()
    source_playlist = AimpPlaylist.from_lines(lines)
    dest_playlist = source_playlist.to_m3u()
    dest_playlist.find_common_path()

    return dest_playlist


def main(args: argparse.ArgumentParser):
    source_playlist: str = args.playlist
    output_dir: Path = Path(args.output)

    if not source_playlist.endswith(".aimppl4"):
        print("Not a supported playlist file (must be a aimppl4 file)")
        return

    with open(source_playlist, "rb") as f:
        source_playlist_data = f.read().decode("utf-16")

    playlist = parse_sections(source_playlist_data)

    final_path = output_dir.joinpath(playlist.filename)

    # print(str(playlist))
    # print(str(final_path))
    # with open(final_path, 'w') as f:
    #     f.write(playlist.to_str())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("playlist",
                        help="The AIMP4 playlist to convert")
    parser.add_argument("-o", "--output",
                        help="The output dir",
                        default=".")

    args = parser.parse_args()
    main(args)
