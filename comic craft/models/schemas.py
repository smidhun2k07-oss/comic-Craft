from pydantic import BaseModel

class PromptRequest(BaseModel):
story_prompt: str
character_name: str = "Alex"
setting: str = "forest"
tone: str = "adventurous"
art_style: str = "anime"
