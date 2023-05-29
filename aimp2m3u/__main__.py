import argparse
from typing import Optional
from pathlib import Path
import os
import sys

from .aimp import AimpPlaylist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("playlist",
                        help="The AIMP4 playlist to convert")
    parser.add_argument("-o", "--output",
                        help="The output dir",
                        default=None)

    args = parser.parse_args()

    source_playlist_path: str = args.playlist
    output_dir: Optional[Path] = args.output

    if output_dir is not None:
        output_dir = Path(output_dir)

    if not source_playlist_path.endswith(".aimppl4"):
        print("Not a supported playlist file (must be a aimppl4 file)")
        return

    aimp_playlist = AimpPlaylist.from_filename(source_playlist_path)
    playlist = aimp_playlist.to_m3u()
    playlist.sanitize_paths()

    common_path = Path(playlist.common_path)

    if output_dir is None:
        output_dir = Path(os.path.join(common_path, "Playlists"))

    final_path = output_dir.joinpath(playlist.filename)

    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Proceed with playlist creation at {final_path}? (Y/n) ",
          end="")
    sys.stdout.flush()  # Need this since there was no '\n' at end of print
    if input().rstrip().lower() not in ("y", ""):
        print("Bailing...")
        return
    print("Proceeding with creation...")

    try:
        with open(final_path, "w") as f:
            f.write(str(playlist))
    except IOError as e:
        print(f"Couldn't write to {final_path}")
        raise e
    print("Done conversion!")
