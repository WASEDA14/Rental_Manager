# utils/formatter.py
def format_currency(amount):
    if amount is None:
        return "0"
    return "{:,}".format(int(amount)).replace(",", ".")


# =====================================#
# =====================================#
# =====================================#
def parse_currency(text):
    if not text:
        return 0
    return int(text.replace(".", "") or 0)


# =====================================#
# =====================================#
# =====================================#
def format_date(date_str):
    if date_str and len(date_str) == 10:
        return f"{date_str[8:10]}/{date_str[5:7]}/{date_str[0:4]}"
    return ""


# =====================================#
# =====================================#
# =====================================#
def parse_date(ddmmyyyy):
    if ddmmyyyy and len(ddmmyyyy) == 10:
        return f"{ddmmyyyy[6:10]}-{ddmmyyyy[3:5]}-{ddmmyyyy[0:2]}"
    return None


def format_money(self, event):
        """Format số tiền có dấu chấm phân cách khi nhập"""
        w = event.widget
        current = w.get()

        # Allow backspace and delete
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End'):
            return

        # Allow only digits and control characters
        if event.char and not event.char.isdigit() and event.char not in ('\b', '\t'):
            return 'break'

        # Get current cursor position
        cursor_pos = w.index('insert')

        # Format the number
        try:
            # Get the raw value (remove all non-digit characters)
            raw = ''.join(c for c in current if c.isdigit())
            if not raw:  # If empty, allow it
                return

            # Format the number with thousand separators
            num = int(raw)
            formatted = format_currency(num)

            # Update the entry
            w.delete(0, 'end')
            w.insert(0, formatted)

            # Set cursor position
            w.icursor(cursor_pos + (len(formatted) - len(current)))
        except ValueError:
            w.delete(0, 'end')

        return 'break'