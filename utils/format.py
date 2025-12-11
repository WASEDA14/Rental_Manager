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