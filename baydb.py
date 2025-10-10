"""
A persistent key-value store that maintains indexes and transaction history.
Uses a simple append-only file format with JSON for storage.

Examples:
    # Basic usage with indexes
    orders = BayDB("orders.json", indexes=["status", ("uniq", True)])

    # Adding records
    orders.set(42, {"product": "T-shirt", "status": "WAIT"})
    orders.set(43, {"product": "Mug", "status": "WAIT"})

    # Auto-generate key
    item = orders.append({"product": "Sticker", "status": "WAIT"})

    # Retrieving records
    record = orders.get(42)  # {'id': 42, 'product': 'T-shirt', 'status': 'WAIT'}

    # Searching by index
    wait_orders = orders.where(status="WAIT")  # list of records
    unique_record = orders.get(uniq=42)  # single record or None

    # Getting all values for an index
    all_statuses = orders.values("status")  # ["WAIT", "PAID"]

    # Updating records
    orders.update(42, status="PAID")

    # Deleting records
    orders.delete(43)

    # Database compaction (reduces file size)
    orders.compact()
"""


import json
import collections
import os


class BayDB:
    def __init__(self, filename, indexes=[], errors='ignore'):
        self.max_id = -1
        self._dict = {}
        self._indexes = {}
        self._unique_indexes = set()
        
        for idx in indexes:
            try:
                index, is_uniq = idx
                if is_uniq:
                    self._unique_indexes.add(index)
            except ValueError:
                index = idx

            if index == "id":
                raise ValueError("Forbidden index name: id")
            self._indexes[index] = collections.defaultdict(set)
                
        self._filename = filename
        self._load(errors)
        self._file = open(self._filename, "a", encoding="utf8")


    def __del__(self):
        if hasattr(self, "_file"):
            self._file.close()


    def _load(self, errors):
        try:
            with open(self._filename, "r") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        action, key = obj[0], int(obj[1])
                        if action == "set":
                            value = obj[2]
                            if "id" in value:
                                del value["id"]
                            self._dict[key] = value
                        elif action == "update":
                            kv = obj[2]
                            for subkey, value in kv.items():
                                if subkey == "id":
                                    continue
                                self._dict[key][subkey] = value
                        elif action == "delete":
                            del self._dict[key]
                    except (ValueError, LookupError):
                        if errors != 'ignore':
                            raise
        except FileNotFoundError:
            pass

        self.max_id = max(self._dict) if self._dict else -1

        for key in self._dict:
            self._update_indexes(key)


    def __contains__(self, key):
        return key in self._dict


    def __iter__(self):
        return ({"id": key} | self.get(key) for key in self._dict)


    def _discard_index(self, index, key):
        if index not in self._indexes:
            return

        value = self._dict.get(key, {}).get(index)
        self._indexes[index][value].discard(key)


    def _discard_indexes(self, key):
        for index in self._indexes:
            self._discard_index(index, key)


    def _update_index(self, index, key):
        if index not in self._indexes:
            return

        if key in self._dict:
            value = self._dict[key].get(index)
            
            if index in self._unique_indexes and value is not None:
                existing_keys = self._indexes[index][value]
                existing_keys_except_current = [k for k in existing_keys if k != key]
                
                if existing_keys_except_current:
                    existing_key = existing_keys_except_current[0]
                    raise ValueError(f"Unique violation for index '{index}' with value '{value}'. "
                                     f"Already used by record with key {existing_key}")
            
            self._indexes[index][value].add(key)


    def _update_indexes(self, key):
        for index in self._indexes:
            self._update_index(index, key)
            

    def _save(self, *args):
        self._file.write(json.dumps(args, ensure_ascii=False) + "\n")
        self._file.flush()


    def append(self, value: dict) -> int:
        if "id" in value:
            raise ValueError("You can't insert element with 'id', use set")

        key = self.max_id + 1
        self.set(key, value)
        return self.get(key)


    def set(self, key: int, value: dict):
        if not isinstance(key, int):
            raise TypeError("Key should be int")
        if not isinstance(value, dict):
            raise TypeError("Value should be dict")
        if "id" in value:
            del value["id"]

        self._discard_indexes(key)
        self.max_id = max(key, self.max_id)
        self._dict[key] = value
        self._update_indexes(key)
        self._save("set", key, value)
        return self.get(key)


    def update(self, key: int, **kwargs):
        if not isinstance(key, int):
            raise TypeError("Key should be int")
        if "id" in kwargs:
            raise ValueError("You can't update id subkey")
        if key not in self._dict:
            raise KeyError

        self.max_id = max(key, self.max_id)
        for subkey, value in kwargs.items():
            self._discard_index(subkey, key)
            self._dict[key][subkey] = value
            self._update_index(subkey, key)

        self._save("update", key, kwargs)
        return self.get(key)


    def delete(self, key: int):
        if key in self._dict:
            self._discard_indexes(key)
            old_val = self._dict[key]
            del self._dict[key]
            self._update_indexes(key)
            self._save("delete", key, old_val)
            return old_val


    def get(self, key: int=None, /, **kwargs):
        if "id" in kwargs:
            key = kwargs["id"]

        if key is not None:
            if key not in self._dict:
                return None
            return {"id": key} | self._dict.get(key)
        else:
            if len(kwargs) != 1:
                raise ValueError(f"Get with too many keyword args")

            index, value = next(iter(kwargs.items()))
            if index not in self._unique_indexes:
                raise ValueError(f"No unique index {index} in db")

            ans = ({"id": key} | self.get(key) for key in self._indexes.get(index, {}).get(value, []))
            for i in ans:
                return i


    def where(self, first=False, /, **kwargs) -> list[dict]:
        if len(kwargs) != 1:
            raise ValueError("Bad args in where")

        index, value = next(iter(kwargs.items()))

        if index not in self._indexes:
            raise ValueError(f"No index {index} in db")
        ans = ({"id": key} | self.get(key) for key in self._indexes.get(index, {}).get(value, []))
        if first:
            for a in ans:
                return a
            return None
        return ans


    def keys(self):
        return self._dict.keys()


    def values(self, index) -> list[str]:
        if index not in self._indexes:
            raise ValueError(f"No index {index} in db")
        return self._indexes.get(index, {}).keys()


    def snapshot(self, filename):
        with open(filename, "w") as f:
            for k, v in self._dict.items():
                f.write(json.dumps(["set", k, v], ensure_ascii=False) + "\n")


    def compact(self, file_suffix=".tmp"):
        tmp_file = self._filename + file_suffix
        self.snapshot(tmp_file)
        os.rename(tmp_file, self._filename)
        self._file.close()
        self._file = open(self._filename, "a", encoding="utf8")
