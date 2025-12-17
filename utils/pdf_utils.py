from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os
import sys

def register_font(font_path, font_name=None):
    """Helper function to register a font with error handling"""
    try:
        if not font_name:
            font_name = os.path.splitext(os.path.basename(font_path))[0]
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        return font_name
    except Exception as e:
        print(f"Warning: Could not register font {font_path}: {str(e)}")
        return None

def get_system_fonts():
    """Find and register system fonts with better fallbacks"""
    # Default fallback fonts
    default_font = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    # Common font paths by OS
    font_paths = []
    
    if sys.platform.startswith('win'):
        # Windows font paths
        font_paths.extend([
            ('C:/Windows/Fonts/arial.ttf', 'Arial', None),
            ('C:/Windows/Fonts/arialbd.ttf', 'Arial-Bold', None),
            ('C:/Windows/Fonts/ARIALUNI.TTF', 'ArialUnicode', None),  # Arial Unicode MS
            ('C:/Windows/Fonts/times.ttf', 'Times-Roman', None),
            ('C:/Windows/Fonts/timesbd.ttf', 'Times-Bold', None),
            ('C:/Windows/Fonts/msyh.ttf', 'MicrosoftYaHei', None),  # Microsoft YaHei (Chinese font that supports Vietnamese)
            ('C:/Windows/Fonts/msyhbd.ttf', 'MicrosoftYaHei-Bold', None),
        ])
    
    # Try to register fonts
    registered_fonts = {}
    
    for font_path, font_name, _ in font_paths:
        if os.path.exists(font_path):
            registered_name = register_font(font_path, font_name)
            if registered_name:
                registered_fonts[font_name] = registered_name
    
    # Set default and bold fonts based on what we found
    if 'ArialUnicode' in registered_fonts:
        default_font = 'ArialUnicode'
        bold_font = 'ArialUnicode'  # We'll use fake bold if needed
    elif 'Arial' in registered_fonts:
        default_font = 'Arial'
        bold_font = 'Arial-Bold' if 'Arial-Bold' in registered_fonts else 'Arial'
    elif 'MicrosoftYaHei' in registered_fonts:
        default_font = 'MicrosoftYaHei'
        bold_font = 'MicrosoftYaHei-Bold' if 'MicrosoftYaHei-Bold' in registered_fonts else 'MicrosoftYaHei'
    
    # Try to register built-in CID fonts as last resort
    if default_font == 'Helvetica':
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            default_font = 'STSong-Light'
            bold_font = 'STSong-Light'
        except:
            pass
    
    return default_font, bold_font

# Get system fonts
DEFAULT_FONT, BOLD_FONT = get_system_fonts()

# Print debug info
print(f"Using fonts - Regular: {DEFAULT_FONT}, Bold: {BOLD_FONT}")

# Register a fake bold font if we don't have a proper bold font
if BOLD_FONT == DEFAULT_FONT:
    try:
        # Create a fake bold style by using the same font with bold weight
        from reportlab.lib.styles import _baseFontNameB
        _baseFontNameB[DEFAULT_FONT] = f'{DEFAULT_FONT}-Bold'
        pdfmetrics.registerFont(TTFont(f'{DEFAULT_FONT}-Bold', pdfmetrics.getFont(DEFAULT_FONT).face))
        BOLD_FONT = f'{DEFAULT_FONT}-Bold'
    except Exception as e:
        print(f"Warning: Could not create fake bold font: {str(e)}")

# Define styles
styles = getSampleStyleSheet()

# Function to safely add a style if it doesn't exist
def add_style(name, **kwargs):
    if name not in styles:
        styles.add(ParagraphStyle(name=name, **kwargs))
    else:
        # Update existing style with new properties
        style = styles[name]
        for key, value in kwargs.items():
            setattr(style, key, value)

# First, create a base Normal style
add_style(
    'Normal',
    fontName=DEFAULT_FONT,
    fontSize=11,
    leading=14,
    spaceAfter=6,
    encoding='UTF-8'
)

# Then create other styles that might inherit from it
add_style(
    'Title',
    parent=styles['Normal'],
    fontName=DEFAULT_FONT,
    fontSize=16,
    alignment=1,  # Center aligned
    spaceAfter=20,
    leading=20,
    textColor=colors.black
)

add_style(
    'Header',
    parent=styles['Normal'],
    fontName=DEFAULT_FONT,
    fontSize=12,
    spaceAfter=10,
    leading=14,
    textColor=colors.black
)

add_style(
    'Bold',
    parent=styles['Normal'],
    fontName=BOLD_FONT,
    spaceAfter=6,
    textColor=colors.black
)

add_style(
    'CustomNormal',
    parent=styles['Normal'],
    fontName=DEFAULT_FONT,
    fontSize=10,
    leading=12,
    textColor=colors.black
)

add_style(
    'Bold',
    fontName=f'{DEFAULT_FONT}-Bold',
    fontSize=10,
    leading=12
)

def format_currency(amount):
    """Format number as VND currency"""
    return f"{int(amount):,}".replace(",", ".") + " VNĐ"

def create_bill_pdf(bill_data, output_path):
    """
    Create a PDF bill
    
    Args:
        bill_data (dict): Dictionary containing bill information
        output_path (str): Path to save the PDF file
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    elements = []
    
    # Add header
    elements.append(Paragraph("HÓA ĐƠN TIỀN PHÒNG", styles['Title']))
    
    # Add company info
    company_info = [
        ["PHÒNG TRỌ GR8"],
        ["Địa chỉ: Số 1, Đường ABC, Quận 1, TP.HCM", f"Mã hóa đơn: {bill_data.get('bill_code', '')}"],
        ["Điện thoại: 0123 456 789", f"Ngày lập: {bill_data.get('created_date', '')}"],
    ]
    
    company_table = Table(company_info, colWidths=[doc.width*0.6, doc.width*0.4])
    company_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), f'{DEFAULT_FONT}'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOLD', (0, 0), (0, 0), True),
        ('FONTNAME', (0, 0), (0, 0), f'{DEFAULT_FONT}-Bold'),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 15))
    
    # Add customer info
    customer_info = [
        ["Khách hàng:", bill_data.get('tenant_name', '')],
        ["Phòng:", bill_data.get('room_name', '')],
        ["Số điện thoại:", bill_data.get('phone', '')],
    ]
    
    customer_table = Table(customer_info, colWidths=[doc.width*0.2, doc.width*0.8])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), f'{DEFAULT_FONT}'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('FONTNAME', (0, 0), (0, -1), f'{DEFAULT_FONT}-Bold'),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 15))
    
    # Add bill details
    details_header = ["STT", "Nội dung", "Số lượng", "Đơn giá", "Thành tiền"]
    details_data = [details_header]
    
    # Add room rent
    details_data.append([
        "1",
        "Tiền phòng tháng " + bill_data.get('bill_month', ''),
        "1 tháng",
        format_currency(bill_data.get('room_rent_amount', 0)),
        format_currency(bill_data.get('room_rent_amount', 0))
    ])
    
    # Add electricity
    elec_usage = bill_data.get('elec_current', 0) - bill_data.get('elec_prev', 0)
    elec_total = elec_usage * bill_data.get('electric_unit_price', 0)
    details_data.append([
        "2",
        f"Tiền điện",
        f"{elec_usage} kWh",
        format_currency(bill_data.get('electric_unit_price', 0)),
        format_currency(elec_total)
    ])
    
    # Add water
    water_usage = bill_data.get('water_current', 0) - bill_data.get('water_prev', 0)
    water_total = water_usage * bill_data.get('water_unit_price', 0)
    details_data.append([
        "3",
        f"Tiền nước",
        f"{water_usage} m³",
        format_currency(bill_data.get('water_unit_price', 0)),
        format_currency(water_total)
    ])
    
    # Add other fees if any
    other_fee = bill_data.get('other_fee', 0)
    if other_fee > 0:
        details_data.append([
            "4",
            bill_data.get('other_fee_note', 'Phí phát sinh'),
            "1",
            format_currency(other_fee),
            format_currency(other_fee)
        ])
    
    # Calculate total
    total = bill_data.get('total_amount', 0)
    
    details_table = Table(details_data, colWidths=[
        20,  # STT
        doc.width*0.4,  # Nội dung
        doc.width*0.15,  # Số lượng
        doc.width*0.15,  # Đơn giá
        doc.width*0.15   # Thành tiền
    ])
    
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), f'{DEFAULT_FONT}'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), f'{DEFAULT_FONT}-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 10))
    
    # Add total
    total_row = [
        ["TỔNG CỘNG:", format_currency(total)],
        ["Số tiền bằng chữ:", f"({number_to_words(total)} đồng)"]
    ]
    
    total_table = Table(total_row, colWidths=[doc.width*0.7, doc.width*0.3])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), f'{DEFAULT_FONT}-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (1, 0), (1, 0), 12),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "<b>Phương thức thanh toán:</b> Tiền mặt hoặc chuyển khoản vào ngày 05 hàng tháng<br/><br/>"
        "<b>Ngân hàng:</b> Vietcombank<br/>"
        "<b>Chi nhánh:</b> Đường Kim Cương<br/>"
        "<b>STK:</b> 0000000001<br/>"
        "<b>Chủ TK:</b> GR8",
        styles['Normal']
    ))

    # Build the PDF
    doc.build(elements)
    return output_path

def create_contract_pdf(contract_data, output_path):
    """
    Create a PDF contract
    
    Args:
        contract_data (dict): Dictionary containing contract information
        output_path (str): Path to save the PDF file
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    elements = []
    
    # Add header
    elements.append(Paragraph("HỢP ĐỒNG CHO THUÊ PHÒNG TRỌ", styles['Title']))
    elements.append(Paragraph("Số: {}".format(contract_data.get('contract_code', '')), styles['Normal']))
    elements.append(Spacer(1, 10))

    
    # Add parties
    elements.append(Paragraph("BÊN CHO THUÊ (BÊN A):", styles['Header']))
    elements.append(Paragraph("PHÒNG TRỌ GR8", styles['Bold']))
    elements.append(Paragraph("Địa chỉ: {}".format(contract_data.get('company_address', 'Số 1, Đường ABC, Quận 1, TP.HCM')), styles['Normal']))
    elements.append(Paragraph("Mã số thuế: 1234567890", styles['Normal']))
    elements.append(Paragraph("Điện thoại: 0123 456 789", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("BÊN THUÊ (BÊN B):", styles['Header']))
    elements.append(Paragraph("Họ và tên: {}".format(contract_data.get('tenant_name', '')), styles['Bold']))
    elements.append(Paragraph("Số CMND/CCCD: {}".format(contract_data.get('id_number', '')), styles['Normal']))
    elements.append(Paragraph("Địa chỉ thường trú: {}".format(contract_data.get('address', '')), styles['Normal']))
    elements.append(Paragraph("Điện thoại: {}".format(contract_data.get('phone', '')), styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Add contract terms
    elements.append(Paragraph("Hai bên cùng thỏa thuận ký kết hợp đồng thuê phòng với các điều khoản sau:", styles['Bold']))
    elements.append(Spacer(1, 10))
    
    # Term 1: Property information
    elements.append(Paragraph("Điều 1: Đối tượng hợp đồng", styles['Bold']))
    elements.append(Paragraph("Bên A cho bên B thuê phòng: {}".format(contract_data.get('room_name', '')), styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Term 2: Rental period
    elements.append(Paragraph("Điều 2: Thời hạn hợp đồng", styles['Bold']))
    elements.append(Paragraph("Từ ngày {} đến ngày {}".format(
        contract_data.get('start_ymd', ''),
        contract_data.get('end_ymd', '')
    ), styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Term 3: Rental price and payment
    elements.append(Paragraph("Điều 3: Giá thuê và phương thức thanh toán", styles['Bold']))
    elements.append(Paragraph("1. Giá thuê phòng: {} / tháng".format(
        format_currency(contract_data.get('rent', 0))
    ), styles['Normal']))
    elements.append(Paragraph("2. Tiền đặt cọc: {}".format(
        format_currency(contract_data.get('deposit', 0))
    ), styles['Normal']))
    elements.append(Paragraph("3. Phương thức thanh toán: Chuyển khoản hoặc tiền mặt vào ngày {} hàng tháng".format(
        contract_data.get('payment_due_day', '05')
    ), styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Term 4: Rights and obligations
    elements.append(Paragraph("Điều 4: Quyền và nghĩa vụ của các bên", styles['Bold']))
    elements.append(Paragraph("1. Quyền và nghĩa vụ của bên A:", styles['Bold']))
    elements.append(Paragraph("- Cung cấp phòng đúng tiêu chuẩn, tiện nghi và trang thiết bị:<br/>""...................................................................................................", styles['Normal']))
    elements.append(Paragraph("2. Quyền và nghĩa vụ của bên B:", styles['Bold']))
    elements.append(Paragraph("- Thanh toán đầy đủ tiền phòng đúng hạn.", styles['Normal']))
    elements.append(Paragraph("- Giữ gìn vệ sinh chung, bảo quản tài sản của phòng.", styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Term 5: Other agreements
    elements.append(Paragraph("Điều 5: Các thỏa thuận khác", styles['Bold']))
    elements.append(Paragraph("1. Hợp đồng này có hiệu lực kể từ ngày ký.", styles['Normal']))
    elements.append(Paragraph("2. Mọi tranh chấp phát sinh sẽ được giải quyết trên tinh thần thỏa thuận.", styles['Normal']))
    elements.append(Paragraph("3. Hợp đồng được lập thành 02 bản, mỗi bên giữ 01 bản có giá trị pháp lý như nhau.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Add signature
    signature = [
        ["ĐẠI DIỆN BÊN A", "BÊN B (KÝ TÊN)"],
        "", "", "", "", "", "",
        ["(Ký, ghi rõ họ tên)", "(Ký, ghi rõ họ tên)"]
    ]
    
    signature_table = Table(signature, colWidths=[doc.width*0.5, doc.width*0.5])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), f'{DEFAULT_FONT}'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSTYLE', (0, 0), (-1, 0), 'Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 8),
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),
        ('LINEABOVE', (1, 0), (1, 0), 1, colors.black),
        ('SPAN', (0, 1), (0, -2)),
        ('SPAN', (1, 1), (1, -2)),
    ]))
    
    elements.append(signature_table)
    
    # Build the PDF
    doc.build(elements)
    return output_path

def number_to_words(number):
    """Convert number to Vietnamese words"""
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    tens = ["", "mười", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", 
            "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    hundreds = ["", "một trăm", "hai trăm", "ba trăm", "bốn trăm", 
                "năm trăm", "sáu trăm", "bảy trăm", "tám trăm", "chín trăm"]
    
    if number == 0:
        return "không"
    
    def convert_less_than_thousand(n):
        if n == 0:
            return ""
        
        result = ""
        hundred = n // 100
        remainder = n % 100
        
        if hundred > 0:
            result += hundreds[hundred] + " "
        
        if remainder > 0:
            if remainder < 10:
                result += "lẻ " + units[remainder]
            elif 10 <= remainder < 20:
                if remainder == 10:
                    result += "mười"
                else:
                    result += "mười " + units[remainder % 10]
            else:
                ten = remainder // 10
                unit = remainder % 10
                result += tens[ten]
                if unit > 0:
                    if unit == 1 and ten >= 2:
                        result += " mốt"
                    elif unit == 4 and ten >= 2:
                        result += " tư"
                    elif unit == 5 and ten >= 2:
                        result += " lăm"
                    elif unit == 5 and ten < 2:
                        result += " năm"
                    else:
                        result += " " + units[unit]
        
        return result.strip()
    
    result = ""
    billion = number // 1000000000
    remainder = number % 1000000000
    
    if billion > 0:
        result += convert_less_than_thousand(billion) + " tỷ "
    
    million = remainder // 1000000
    remainder = remainder % 1000000
    
    if million > 0:
        result += convert_less_than_thousand(million) + " triệu "
    
    thousand = remainder // 1000
    remainder = remainder % 1000
    
    if thousand > 0:
        result += convert_less_than_thousand(thousand) + " nghìn "
    
    if remainder > 0:
        result += convert_less_than_thousand(remainder)
    
    # Remove extra spaces
    result = ' '.join(result.split())
    
    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]
    
    return result
