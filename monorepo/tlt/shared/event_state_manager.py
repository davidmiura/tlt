import json
from pathlib import Path
from typing import Optional, Type, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class EventStateManager:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def _get_event_file(self, guild_id: str, event_id: str) -> Path:
        path = self.root_dir / guild_id / event_id
        path.mkdir(parents=True, exist_ok=True)
        return path / "event.json"

    def _load_event_data(self, guild_id: str, event_id: str) -> dict:
        event_file = self._get_event_file(guild_id, event_id)
        if not event_file.exists():
            return {"event_id": event_id}
        with event_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_event_data(self, guild_id: str, event_id: str, data: dict):
        event_file = self._get_event_file(guild_id, event_id)
        with event_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def add_model_entry(
        self,
        guild_id: str,
        event_id: str,
        model_instance: BaseModel
    ):
        data = self._load_event_data(guild_id, event_id)
        model_key = model_instance.__class__.__name__
        model_list = data.setdefault(model_key, [])
        model_list.append(model_instance.model_dump())
        self._save_event_data(guild_id, event_id, data)

    def list_model_entries(
        self,
        guild_id: str,
        event_id: str,
        model_class: Type[T]
    ) -> List[T]:
        data = self._load_event_data(guild_id, event_id)
        model_key = model_class.__name__
        entries = data.get(model_key, [])
        return [model_class(**entry) for entry in entries]

    def update_model_entry(
        self,
        guild_id: str,
        event_id: str,
        model_instance: BaseModel,
        identifier_field: str
    ):
        data = self._load_event_data(guild_id, event_id)
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
        self._save_event_data(guild_id, event_id, data)

    def delete_model_entry(
        self,
        guild_id: str,
        event_id: str,
        model_class: Type[BaseModel],
        identifier_field: str,
        identifier_value: str
    ):
        data = self._load_event_data(guild_id, event_id)
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
        self._save_event_data(guild_id, event_id, data)

    def list_model_types(
        self,
        guild_id: str,
        event_id: str
    ) -> List[str]:
        data = self._load_event_data(guild_id, event_id)
        return [k for k in data.keys() if k != "event_id"]

    def update_event_field(
        self,
        guild_id: str,
        event_id: str,
        field_name: str,
        field_value: any
    ):
        """Update a single field in the event data"""
        data = self._load_event_data(guild_id, event_id)
        data[field_name] = field_value
        self._save_event_data(guild_id, event_id, data)

    def append_to_array_field(
        self,
        guild_id: str,
        event_id: str,
        array_field_name: str,
        item: any
    ):
        """Append an item to an array field in the event data"""
        data = self._load_event_data(guild_id, event_id)
        if array_field_name not in data:
            data[array_field_name] = []
        elif not isinstance(data[array_field_name], list):
            data[array_field_name] = []
        data[array_field_name].append(item)
        self._save_event_data(guild_id, event_id, data)

    def update_nested_field(
        self,
        guild_id: str,
        event_id: str,
        field_path: str,
        field_value: any
    ):
        """Update a nested field using dot notation (e.g., 'config.setting.value')"""
        data = self._load_event_data(guild_id, event_id)
        
        # Split the field path by dots
        path_parts = field_path.split('.')
        current = data
        
        # Navigate to the parent of the final field
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the final field value
        current[path_parts[-1]] = field_value
        self._save_event_data(guild_id, event_id, data)

    def remove_from_array_field(
        self,
        guild_id: str,
        event_id: str,
        array_field_name: str,
        item_match: dict
    ):
        """Remove items from an array field that match the given criteria"""
        data = self._load_event_data(guild_id, event_id)
        
        if array_field_name not in data or not isinstance(data[array_field_name], list):
            return
        
        original_list = data[array_field_name]
        new_list = []
        
        for item in original_list:
            if isinstance(item, dict):
                # Check if all match criteria are satisfied
                match = True
                for key, value in item_match.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if not match:
                    new_list.append(item)
            else:
                # For non-dict items, only remove if exact match
                if item != item_match:
                    new_list.append(item)
        
        data[array_field_name] = new_list
        self._save_event_data(guild_id, event_id, data)