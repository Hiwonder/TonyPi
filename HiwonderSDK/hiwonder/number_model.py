def render_number(pos0, pos1, pos2, pos3):
    # 每个字符在不同位置的显示模式（16进制编码）
    PATTERNS = {
        '0': (0x00, 0x3E, 0x22, 0x3E),
        '1': (0x00, 0x22, 0x3E, 0x20),
        '2': (0x00, 0x3A, 0x2A, 0x2E),
        '3': (0x00, 0x2A, 0x2A, 0x3E),
        '4': (0x00, 0x0E, 0x08, 0x3E),
        '5': (0x00, 0x2E, 0x2A, 0x3A),
        '6': (0x00, 0x3E, 0x2A, 0x3A),
        '7': (0x00, 0x02, 0x02, 0x3E),
        '8': (0x00, 0x3E, 0x2A, 0x3E),
        '9': (0x00, 0x2E, 0x2A, 0x3E),
        '.': (0x00, 0x20, 0x00, 0x00),
        '%': {
            2: (0x00, 0x00, 0x26, 0x16),
            3: (0x08, 0x34, 0x32, 0x00)
        }
    }

    display_buf = [0x00] * 16  # 初始化16字节的显示缓冲区

    # 遍历每个位置并填充数据
    for idx, char in enumerate([pos0, pos1, pos2, pos3]):
        if char == '-':
            continue
        
        start = idx * 4  # 每个位置占据4个字节
        
        # 特殊处理百分号
        if char == '%':
            if idx == 2:
                display_buf[8:12] = PATTERNS['%'][2]
            elif idx == 3:
                display_buf[12:16] = PATTERNS['%'][3]
            continue
        
        # 普通字符处理
        if char in PATTERNS:
            display_buf[start:start+4] = PATTERNS[char]

    return tuple(display_buf)