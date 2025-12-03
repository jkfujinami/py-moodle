# PyMoodle

**PyMoodle** は、[Moodle](https://moodle.org/) LMS プラットフォームと対話するための、非公式の Python クライアントライブラリです。Moodle の Web インターフェースをスクレイピングすることで、コース情報の取得、課題の確認、ファイルのダウンロード、小テスト結果の閲覧などをプログラムから行うことができます。

## 主な機能

*   **認証の自動化**: ログインフローを処理し、セッションを自動的に維持します。
*   **セッションの永続化**: セッション Cookie をローカルの JSON ファイルに保存し、再ログインの手間を省きます。
*   **コース管理**: 登録しているコースの一覧や、コースカテゴリを閲覧できます。
*   **コンテンツの抽出**:
    *   **課題 (Assignments)**: 提出期限、提出状況、添付ファイルへのリンクを取得します。
    *   **小テスト (Quizzes)**: 受験履歴、評点、フィードバックを確認できます。
    *   **リソース**: ファイルやフォルダの直接ダウンロード URL を解決します。
    *   **フォーラム & ページ**: コンテンツや概要を抽出します。
*   **ファイルダウンロード**: コース資料や提出ファイルをダウンロードするためのヘルパーメソッドを提供します。

## 必要要件

*   Python 3.8 以上
*   `requests`
*   `beautifulsoup4`

## インストール

ソースコードから直接インストールできます：

```bash
git clone https://github.com/jkfujinami/py-moodle.git
cd py-moodle
pip install -e .
```

## 使い方

### 1. 初期化とログイン

Moodle のベース URL を指定してクライアントを初期化します。指定しない場合は、デフォルトの設定(舞鶴高専)が使用されます。

```python
from pymoodle import MoodleClient
import getpass

# あなたの Moodle URL で初期化
# 注意: URL の末尾にはスラッシュを付けてください
BASE_URL = "https://moodle.example.com/"
client = MoodleClient(session_file="session.json", base_url=BASE_URL)

# 有効なセッションが保存されているか確認
if client.is_logged_in():
    print("ファイルからセッションを復元しました。")
else:
    # ログインを実行
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    if client.login(username, password):
        print("ログインに成功しました。")
    else:
        print("ログインに失敗しました。")
        exit(1)
```

### 2. コースの取得

登録されているコースの一覧を取得します。

```python
courses = client.get_my_courses()
print(f"{len(courses)} 個のコースが見つかりました:")

for course in courses:
    print(f"- {course['name']} (ID: {course['id']})")
```

### 3. コースコンテンツの閲覧

特定のコース内のセクションとモジュールを反復処理します。

```python
course_id = 12345
sections = client.get_course_contents(course_id)

for section in sections:
    print(f"\n### {section['name']} ###")
    for module in section['modules']:
        status = "[x]" if module['completed'] else "[ ]"
        print(f"{status} {module['name']} ({module['type']})")

        # 例: 課題 (Assign) の処理
        if module['type'] == 'assign':
            details = client.get_assignment_details(module['id'])
            if details:
                print(f"    期限: {details['due_date']}")
                print(f"    状態: {details['submission_status']}")
```

### 4. ファイルのダウンロード

フォルダリソースや直接リンクからファイルをダウンロードします。

```python
output_dir = "./downloads"

# 例: フォルダモジュール内の全ファイルをダウンロード
if module['type'] == 'folder':
    details = client.get_folder_details(module['id'])
    if details:
        for file_item in details['files']:
            print(f"{file_item['filename']} をダウンロード中...")
            client.download_file(file_item['url'], output_dir)
```

## API リファレンス

### `MoodleClient`

ライブラリのメインエントリーポイントです。

*   `__init__(session_file="session.json", base_url=None)`
*   `login(username, password) -> bool`
*   `is_logged_in() -> bool`
*   `get_my_courses() -> List[Course]`
*   `get_course_contents(course_id) -> List[Section]`
*   `get_course_categories(category_id=None) -> List[Category]`

### コンテンツ取得メソッド

*   `get_assignment_details(assign_id)`
*   `get_quiz_details(quiz_id)`
*   `get_folder_details(folder_id)`
*   `get_page_details(page_id)`
*   `get_forum_details(forum_id)`
*   `get_resource_download_url(resource_id)`
*   `get_external_url(url_id)`

### ユーティリティ

*   `download_file(url, save_path)`

## エラーハンドリング

PyMoodle は `pymoodle.exceptions` でカスタム例外を提供しています：

*   `MoodleLoginError`: 認証に失敗した場合。
*   `MoodleRequestError`: ネットワークや HTTP エラーが発生した場合。
*   `MoodleParseError`: HTML レスポンスの解析に失敗した場合（Moodle のテーマの違いなどが原因の可能性があります）。

```python
from pymoodle.exceptions import MoodleLoginError

try:
    client.login(user, pwd)
except MoodleLoginError as e:
    print(f"認証エラー: {e}")
```

## 免責事項

このライブラリは **非公式** であり、Moodle HQ とは提携していません。Web スクレイピングに依存しているため、以下の点に注意してください：
1.  Moodle のテーマや DOM 構造が大幅に変更された場合、**動作しなくなる可能性**があります。
2.  **全て自己責任でお願いします。**

## ライセンス

[MIT License](LICENSE)
