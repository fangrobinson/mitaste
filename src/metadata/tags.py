import eyed3
from typing import Optional, Dict, Any, Union
from pathlib import Path


class TagManager:
    """A library for managing audio file metadata tags with support for partial updates."""
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize TagManager with an audio file.
        
        Args:
            file_path: Path to the audio file
        """
        self.file_path = Path(file_path)
        self.audiofile = None
        self._load_file()
    
    def _load_file(self) -> None:
        """Load the audio file and initialize tag if needed."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.file_path}")
        
        self.audiofile = eyed3.load(str(self.file_path))
        if self.audiofile is None:
            raise ValueError(f"Unable to load audio file: {self.file_path}")
        
        if self.audiofile.tag is None:
            self.audiofile.initTag()
    
    def update_basic_tags(self, **kwargs) -> None:
        """
        Update basic metadata tags. Only specified tags will be updated.
        
        Args:
            **kwargs: Tag names and values (e.g., artist="Artist Name", title="Song Title")
        """
        valid_tags = {
            'artist', 'album', 'title', 'track_num', 'year', 
            'genre', 'composer', 'album_artist', 'disc_num'
        }
        
        for tag_name, value in kwargs.items():
            if tag_name in valid_tags and hasattr(self.audiofile.tag, tag_name):
                setattr(self.audiofile.tag, tag_name, value)
            else:
                print(f"Warning: Invalid or unsupported tag '{tag_name}'")
    
    def set_album_art(self, image_path: Union[str, Path], 
                     picture_type: int = eyed3.id3.frames.ImageFrame.FRONT_COVER,
                     mime_type: str = "image/jpeg",
                     description: str = "Cover Art") -> None:
        """
        Set album art for the audio file.
        
        Args:
            image_path: Path to the image file (JPEG/PNG)
            picture_type: Type of picture (default: front cover)
            mime_type: MIME type of the image (default: image/jpeg)
            description: Description of the image (default: Cover Art)
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(image_path, "rb") as img_fp:
            image_data = img_fp.read()
            self.audiofile.tag.images.set(
                picture_type,
                image_data,
                mime_type,
                description
            )
    
    def get_tags(self) -> Dict[str, Any]:
        """
        Get all current tags from the audio file.
        
        Returns:
            Dictionary containing all available tags
        """
        tags = {}
        if self.audiofile.tag:
            for attr in dir(self.audiofile.tag):
                if not attr.startswith('_') and not callable(getattr(self.audiofile.tag, attr)):
                    value = getattr(self.audiofile.tag, attr)
                    if value is not None:
                        tags[attr] = value
        return tags
    
    def has_album_art(self) -> bool:
        """
        Check if the audio file has album art.
        
        Returns:
            True if album art exists, False otherwise
        """
        return len(self.audiofile.tag.images) > 0
    
    def remove_album_art(self, picture_type: Optional[int] = None) -> None:
        """
        Remove album art from the audio file.
        
        Args:
            picture_type: Specific picture type to remove (None removes all)
        """
        if picture_type is None:
            self.audiofile.tag.images.clear()
        else:
            # Remove specific picture type
            images_to_keep = []
            for img in self.audiofile.tag.images:
                if img.pictureType != picture_type:
                    images_to_keep.append(img)
            self.audiofile.tag.images = images_to_keep
    
    def save(self) -> None:
        """Save all changes to the audio file."""
        if self.audiofile.tag:
            self.audiofile.tag.save()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically save changes."""
        if exc_type is None:
            self.save()


# Convenience functions for quick operations
def update_tags(file_path: Union[str, Path], **kwargs) -> None:
    """
    Quick function to update tags on an audio file.
    
    Args:
        file_path: Path to the audio file
        **kwargs: Tag names and values to update
    """
    with TagManager(file_path) as manager:
        manager.update_basic_tags(**kwargs)


def set_cover_art(file_path: Union[str, Path], image_path: Union[str, Path]) -> None:
    """
    Quick function to set album art on an audio file.
    
    Args:
        file_path: Path to the audio file
        image_path: Path to the image file
    """
    with TagManager(file_path) as manager:
        manager.set_album_art(image_path)


def get_audio_tags(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Quick function to get all tags from an audio file.
    
    Args:
        file_path: Path to the audio file
    
    Returns:
        Dictionary containing all available tags
    """
    with TagManager(file_path) as manager:
        return manager.get_tags()

