def format_currency(amount):
    """Chuyển số thành chuỗi tiền Việt Nam (dấu chấm phân cách)"""
    if amount is None or amount == 0:
        return "0"
    return "{:,}".format(int(amount)).replace(",", ".")


def parse_currency(text):
    """Chuyển chuỗi tiền về số nguyên (bỏ hết dấu chấm)"""
    if not text:
        return 0
    cleaned = ''.join(c for c in str(text) if c.isdigit())
    return int(cleaned) if cleaned else 0


def format_money(event):
    """
    Format số tiền realtime khi gõ/xóa (rất mượt với Backspace)
    Sử dụng <KeyRelease> hoặc <KeyPress> đều được, nhưng KeyRelease thường ổn hơn
    """
    widget = event.widget

    # Cho phép các phím điều khiển di chuyển con trỏ
    if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab'):
        # Vẫn để Tkinter xử lý xóa trước, sau đó format lại ở KeyRelease
        return None

    # Chặn mọi ký tự không phải số
    if event.keysym not in ('BackSpace', 'Delete') and (not event.char or not event.char.isdigit()):
        return "break"

    # Lấy text hiện tại SAU khi phím đã được xử lý (ở KeyRelease)
    current = widget.get()

    try:
        # Lưu vị trí con trỏ trước khi format
        cursor_pos = widget.index("insert")

        # Chuyển về số nguyên
        number = parse_currency(current)

        # Format lại
        formatted = format_currency(number)

        # Nếu không thay đổi gì thì không cần làm lại (tránh loop vô ích)
        if formatted == current:
            return None

        # Cập nhật text
        widget.delete(0, "end")
        widget.insert(0, formatted)

        # Điều chỉnh vị trí con trỏ cho tự nhiên hơn khi xóa/gõ
        # Khi backspace thường con trỏ nên ở vị trí cũ hoặc gần đó
        len_diff = len(formatted) - len(current)
        new_pos = cursor_pos + len_diff

        # Giới hạn vị trí hợp lý
        if new_pos < 0:
            new_pos = 0
        elif new_pos > len(formatted):
            new_pos = len(formatted)

        widget.icursor(new_pos)

    except Exception:
        # An toàn: nếu có lỗi gì thì xóa sạch
        widget.delete(0, "end")

    return None  # Không break ở KeyRelease để cho phép xóa bình thường