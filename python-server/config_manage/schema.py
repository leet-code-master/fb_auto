from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class ConfigItem(BaseModel):
    key: str = Field(..., description="配置键")
    value: Any = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    
class ConfigUpdateRequest(BaseModel):
    items: Dict[str, Any] = Field(..., description="配置项字典")
    
class ConfigResponse(BaseModel):
    success: bool
    message: str = ""
    data: Optional[Dict[str, ConfigItem]] = None    