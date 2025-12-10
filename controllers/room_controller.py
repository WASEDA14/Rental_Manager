from services.room_service import RoomModel, RoomDTO
from tkinter import messagebox


class RoomController:
    def __init__(self, view):
        self.view = view
        self.model = RoomModel()

        # gắn callback từ view
        self.view.set_controller(self)

        # load list ban đầu
        self.refresh_list()

    def refresh_list(self):
        rooms = self.model.list()
        self.view.show_room_list(rooms)

    def add_room(self):
        data = self.view.get_form_values()   # view trả dict
        room_id = data["room_id"].strip()
        room_name = data["room_name"].strip()

        if not room_id or not room_name:
            messagebox.showerror("Lỗi", "Room ID và Room Name không được trống")
            return

        dto = RoomDTO(
            room_id=room_id,
            room_name=room_name,
            base_rent=int(data["base_rent"] or 0),
            area_m2=float(data["area_m2"] or 0) if data["area_m2"] else None,
            floor=int(data["floor"] or 0) if data["floor"] else None,
            electric_unit_price=int(data["electric_unit_price"] or 0) if data["electric_unit_price"] else None,
            water_unit_price=int(data["water_unit_price"] or 0) if data["water_unit_price"] else None,
            status=data.get("status") or "AVAILABLE",
            note=data.get("note") or ""
        )

        try:
            self.model.add(dto)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thêm được phòng:\n{e}")
            return

        self.refresh_list()
        self.view.clear_form()

    def delete_room(self):
        room_id = self.view.get_selected_room_id()
        if not room_id:
            messagebox.showwarning("Thông báo", "Chọn 1 phòng để xoá")
            return

        self.model.soft_delete(room_id)
        self.refresh_list()
