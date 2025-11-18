# fake/in-memory, thay bằng DB sau
from dataclasses import dataclass

@dataclass
class RoomDTO:
    id: int | None
    code: str
    base_rent: int
    is_active: bool = True

class RoomService:
    def __init__(self):
        self._auto = 1
        self._data: list[RoomDTO] = []

    def list(self, keyword: str|None=None) -> list[RoomDTO]:
        data = self._data
        if keyword:
            kw = keyword.lower()
            data = [r for r in data if kw in r.code.lower()]
        return data

    def create(self, code: str, base_rent: int, is_active: bool) -> RoomDTO:
        if any(r.code == code for r in self._data):
            raise ValueError("Số phòng đã tồn tại")
        dto = RoomDTO(id=self._auto, code=code, base_rent=base_rent, is_active=is_active)
        self._auto += 1
        self._data.append(dto)
        return dto

    def update(self, room_id: int, code: str, base_rent: int, is_active: bool) -> RoomDTO:
        for r in self._data:
            if r.id == room_id:
                # chặn trùng code với phòng khác
                if code != r.code and any(x.code == code for x in self._data):
                    raise ValueError("Số phòng đã tồn tại")
                r.code, r.base_rent, r.is_active = code, base_rent, is_active
                return r
        raise ValueError("Không tìm thấy phòng")

    def delete(self, room_id: int) -> None:
        self._data = [r for r in self._data if r.id != room_id]
