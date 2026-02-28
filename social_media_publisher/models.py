from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class AuthConfig:
    cookie_file: Optional[str] = None
    profile_path: Optional[str] = None
    # Add other auth methods (e.g., API keys) as needed

@dataclass
class PostContent:
    title: str
    body: str
    hashtags: List[str] = field(default_factory=list)
    image_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SocialPost:
    platform: str
    auth: AuthConfig
    content: PostContent
