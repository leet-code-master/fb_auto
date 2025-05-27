from .schema import ConfigItem, ConfigUpdateRequest, ConfigResponse
import json
import os
from typing import Dict

class ConfigService:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, ConfigItem]:
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {key: ConfigItem(**value) for key, value in data.items()}
            return {}
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            return {}
            
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({key: item.dict() for key, item in self.config.items()}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            
    def get_all_config(self) -> ConfigResponse:
        """获取所有配置"""
        return ConfigResponse(
            success=True,
            data=self.config,
            message="获取配置成功"
        )
        
    def update_config(self, request: ConfigUpdateRequest) -> ConfigResponse:
        """更新配置"""
        try:
            for key, value in request.items.items():
                if key in self.config:
                    self.config[key].value = value
                else:
                    self.config[key] = ConfigItem(
                        key=key,
                        value=value,
                        description=f"自动创建的配置项 {key}"
                    )
            
            self._save_config()
            return ConfigResponse(
                success=True,
                message="配置更新成功"
            )
        except Exception as e:
            return ConfigResponse(
                success=False,
                message=f"配置更新失败: {str(e)}"
            )
            
    def get_config(self, key: str) -> ConfigResponse:
        """获取单个配置项"""
        if key in self.config:
            return ConfigResponse(
                success=True,
                data={key: self.config[key]},
                message="获取配置成功"
            )
        else:
            return ConfigResponse(
                success=False,
                message=f"配置项 {key} 不存在"
            )    