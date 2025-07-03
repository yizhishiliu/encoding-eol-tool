import chardet

def detect_encoding(file_path, sample_size=10000):
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    return result['encoding'], result['confidence']


def detect_eol(file_path, encoding):
    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        content = f.read()

    crlf = content.count('\r\n')
    lf = content.count('\n')
    cr = content.count('\r') - crlf

    if crlf > lf and crlf > cr:
        return 'CRLF (\\r\\n)'
    elif lf > crlf and lf > cr:
        return 'LF (\\n)'
    elif cr > crlf and cr > lf:
        return 'CR (\\r)'
    else:
        return '未知'


def convert_file(file_path, target_encoding='utf-8', target_eol='\n'):
    try:
        original_encoding, _ = detect_encoding(file_path)
        with open(file_path, 'r', encoding=original_encoding, errors='ignore') as f:
            content = f.read()

        # 标准化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        if target_eol != '\n':
            content = content.replace('\n', target_eol)

        # 备份原文件
        backup_path = file_path + ".bak"
        with open(backup_path, 'w', encoding=original_encoding, newline='') as f:
            f.write(content)

        # 写入目标编码/换行符的新文件
        with open(file_path, 'w', encoding=target_encoding, newline='') as f:
            f.write(content)

        return True, None
    except Exception as e:
        return False, str(e)
