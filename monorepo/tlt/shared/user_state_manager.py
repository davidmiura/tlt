import json
from pathlib import Path
from typing import Optional, Type, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class UserStateManager:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def _get_user_file(self, guild_id: str, event_id: str, user_id: str) -> Path:
        path = self.root_dir / guild_id / event_id / user_id
        path.mkdir(parents=True, exist_ok=True)
        return path / "user.json"

    def _load_user_data(self, guild_id: str, event_id: str, user_id: str) -> dict:
        user_file = self._get_user_file(guild_id, event_id, user_id)
        if not user_file.exists():
            return {"user_id": user_id}
        with user_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_user_data(self, guild_id: str, event_id: str, user_id: str, data: dict):
        user_file = self._get_user_file(guild_id, event_id, user_id)
        with user_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def add_model_entry(
        self,
        guild_id: str,
        event_id: str,
        user_id: str,
        model_instance: BaseModel
    ):
        data = self._load_user_data(guild_id, event_id, user_id)
        model_key = model_instance.__class__.__name__
        model_list = data.setdefault(model_key, [])
        model_list.append(model_instance.model_dump())
        self._save_user_data(guild_id, event_id, user_id, data)

    def list_model_entries(
        self,
        guild_id: str,
        event_id: str,
        user_id: str,
        model_class: Type[T]
    ) -> List[T]:
        data = self._load_user_data(guild_id, event_id, user_id)
        model_key = model_class.__name__
        entries = data.get(model_key, [])
        return [model_class(**entry) for entry in entries]

    def update_model_entry(
        self,
        guild_id: str,
        event_id: str,
        user_id: str,
        model_instance: BaseModel,
        identifier_field: str
    ):
        data = self._load_user_data(guild_id, event_id, user_id)
        model_key = model_instance.__class__.__name__
        identifier_value = getattr(model_instance, identifier_field)

        entries = data.get(model_key, [])
        updated = False

        for i, entry in enumerate(entries):
            if entry.get(identifier_field) == identifier_value:
                entries[i] = model_instance.model_dump()
                updated = True
                break

        if not updated:
            raise ValueError(
                f"No entry with {identifier_field}={identifier_value} found in {model_key}."
            )

        data[model_key] = entries
        self._save_user_data(guild_id, event_id, user_id, data)

    def delete_model_entry(
        self,
        guild_id: str,
        event_id: str,
        user_id: str,
        model_class: Type[BaseModel],
        identifier_field: str,
        identifier_value: str
    ):
        data = self._load_user_data(guild_id, event_id, user_id)
        model_key = model_class.__name__
        original_list = data.get(model_key, [])
        new_list = [
            entry for entry in original_list
            if entry.get(identifier_field) != identifier_value
        ]

        if len(new_list) == len(original_list):
            raise ValueError(
                f"No entry with {identifier_field}={identifier_value} found in {model_key}."
            )

        data[model_key] = new_list
        self._save_user_data(guild_id, event_id, user_id, data)

    def list_model_types(
        self,
        guild_id: str,
        event_id: str,
        user_id: str
    ) -> List[str]:
        data = self._load_user_data(guild_id, event_id, user_id)
        return [k for k in data.keys() if k != "user_id"]