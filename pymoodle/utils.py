import os
import re
from urllib.parse import unquote, urlparse
from typing import Optional

def extract_filename_from_response(response, url: str) -> str:
    """
    Extract filename from Content-Disposition header or URL.
    """
    filename = ""
    # Content-Dispositionヘッダーからファイル名を取得
    if "Content-Disposition" in response.headers:
        # filename="example.pdf" または filename*=UTF-8''example.pdf などを解析
        cd = response.headers["Content-Disposition"]
        matches = re.findall(r'filename\*=UTF-8\'\'(.+)|filename="([^"]+)"|filename=([^;]+)', cd)
        if matches:
            # マッチしたグループのどれかを採用
            for match in matches[0]:
                if match:
                    filename = unquote(match)
                    break

    # ヘッダーになければURLから取得
    if not filename:
        parsed = urlparse(url)
        filename = unquote(os.path.basename(parsed.path))

    if not filename:
        filename = "downloaded_file"

    return filename
