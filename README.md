# PyMoodle (Unofficial Moodle API Client)

舞鶴高専Moodle (https://moodle2.maizuru-ct.ac.jp/moodle/) 向けの非公式APIクライアントライブラリです。
スクレイピングを使用して、コース一覧、コースコンテンツ、課題情報、小テスト結果などを取得し、ファイルのダウンロードも可能です。

## 特徴

*   **セッション永続化**: 一度ログインすると、セッションCookieをJSONファイルに保存し、次回以降のログインを省略できます。
*   **コース情報取得**: マイコース一覧、カテゴリ一覧を取得できます。
*   **詳細なコンテンツ解析**:
    *   **課題 (Assign)**: 提出期限、ステータス、添付ファイル
    *   **小テスト (Quiz)**: 受験履歴、評点、フィードバック
    *   **フォルダ (Folder)**: ファイルリスト
    *   **ページ (Page)**: コンテンツ内容
    *   **フォーラム (Forum)**: 概要
*   **ファイルダウンロード**: 配布資料やフォルダ内のファイルをローカルに保存できます。
*   **リソース解決**: 外部リンクの実体URLなどを解決します。

## 必要要件

*   Python 3.8+
*   requests
*   beautifulsoup4

## インストール

```bash
pip install -e .
```

## 使い方

### 基本的な使用例

```python
from pymoodle.client import MoodleClient
import getpass
import os

# クライアントの初期化
# base_urlを指定しない場合は舞鶴高専Moodleがデフォルトになります
client = MoodleClient(session_file="moodle_session.json")

# 別のMoodleサイトを利用する場合:
# client = MoodleClient(session_file="other_session.json", base_url="https://moodle.example.com/")

# ログイン処理（省略可能、セッションがあれば自動でログイン状態になる）
if not client.is_logged_in():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    client.login(username, password)

# コースコンテンツの取得と詳細情報の表示
course_id = 12345  # 任意のコースID
sections = client.get_course_contents(course_id)

for section in sections:
    print(f"Section: {section['name']}")
    for mod in section['modules']:
        print(f"  - {mod['name']} ({mod['type']})")

        # 課題の詳細取得
        if mod['type'] == 'assign' and mod['id']:
            details = client.get_assignment_details(mod['id'])
            if details:
                print(f"    Due: {details['due_date']}, Status: {details['submission_status']}")

        # 小テストの詳細取得
        elif mod['type'] == 'quiz' and mod['id']:
            details = client.get_quiz_details(mod['id'])
            if details and details['attempts']:
                print(f"    Grade: {details['attempts'][-1]['grade']}")

        # フォルダ内のファイルをダウンロード
        elif mod['type'] == 'folder' and mod['id']:
            details = client.get_folder_details(mod['id'])
            if details:
                for file_item in details['files']:
                    print(f"    Downloading {file_item['filename']}...")
                    client.download_file(file_item['url'], "downloads")
```

### 機能一覧

*   `client.login(username, password)`: ログインします。
*   `client.get_my_courses()`: 登録されているコース一覧を取得します。
*   `client.get_course_contents(course_id)`: コース内のセクションとモジュール一覧を取得します。
*   **詳細情報取得**:
    *   `client.get_assignment_details(assign_id)`: 課題の詳細（期限、ステータスなど）を取得。
    *   `client.get_quiz_details(quiz_id)`: 小テストの詳細（受験履歴、評点など）を取得。
    *   `client.get_folder_details(folder_id)`: フォルダ内のファイル一覧を取得。
    *   `client.get_page_details(page_id)`: ページの内容を取得。
    *   `client.get_forum_details(forum_id)`: フォーラムの概要を取得。
*   **ユーティリティ**:
    *   `client.download_file(url, save_path)`: ファイルをダウンロードして保存します。
    *   `client.get_resource_download_url(resource_id)`: 配布資料（PDFなど）の直接ダウンロードURLを取得。
    *   `client.get_external_url(url_id)`: 外部リンクの実体URLを取得。

## ディレクトリ構成

*   `pymoodle/`: ライブラリ本体
    *   `client.py`: ユーザー向けAPIクライアント (Facade)
    *   `core.py`: 基本的なHTTP通信とセッション管理
    *   `services.py`: ビジネスロジック
    *   `parsers.py`: HTML解析ロジック
    *   `types.py`: 型定義
*   `example.py`: サンプルコード

## 注意事項

*   本ライブラリは非公式であり、Moodleの仕様変更により動作しなくなる可能性があります。
*   スクレイピングを行うため、サーバーに過度な負荷をかけないように注意してください。
