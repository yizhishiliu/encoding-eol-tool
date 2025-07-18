import chardet

def detect_encoding(file_path, sample_size=10000):
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    return result['encoding'], result['confidence']

def detect_eol(file_path, encoding='utf-8'):
    """
    检测文件的换行符类型
    :param file_path: 文件路径
    :param encoding: 文件编码，默认为utf-8，仅用于日志记录，不影响检测逻辑
    :return: 换行符类型的显示名称
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    crlf_count = data.count(b'\r\n')
    # 注意：先移除已统计的 \r\n，再统计单独的 \n 和 \r
    temp = data.replace(b'\r\n', b'')
    lf_count = temp.count(b'\n')
    cr_count = temp.count(b'\r')

    if crlf_count > 0 and lf_count == 0 and cr_count == 0:
        return 'CRLF (\\r\\n)'
    elif lf_count > 0 and crlf_count == 0 and cr_count == 0:
        return 'LF (\\n)'
    elif cr_count > 0 and crlf_count == 0 and lf_count == 0:
        return 'CR (\\r)'
    else:
        # 混合情况
        parts = []
        if crlf_count > 0:
            parts.append('CRLF')
        if lf_count > 0:
            parts.append('LF')
        if cr_count > 0:
            parts.append('CR')
        return '混合换行符: ' + ', '.join(parts)

def convert_file(file_path, target_encoding='utf-8', target_eol='\n'):
    try:
        original_encoding, _ = detect_encoding(file_path)

        # 尝试将 chardet 推测的编码转换为 Python 支持的编码
        python_encodings = {
            'Windows-1252': 'windows-1252',
            'ISO-8859-1': 'iso-8859-1',
            'UTF-8': 'utf-8',
            'UTF-16': 'utf-16',
            'UTF-16BE': 'utf-16-be',
            'UTF-16LE': 'utf-16-le',
        }
        encoding = python_encodings.get(original_encoding, 'utf-8')

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        # 标准化换行符
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        if target_eol != '\n':
            content = content.replace('\n', target_eol)

        # 备份原文件
        backup_path = file_path + ".bak"
        with open(backup_path, 'w', encoding=encoding, newline='') as f:
            f.write(content)

        # 写入目标编码/换行符的新文件
        with open(file_path, 'w', encoding=target_encoding, newline='') as f:
            f.write(content)

        return True, None
    except Exception as e:
        return False, str(e)