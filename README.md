# PyMoodle

**PyMoodle** は、[Moodle](https://moodle.org/) LMS の、非公式の Python クライアントライブラリです。Moodle の Web インターフェースをスクレイピングすることで、コース情報の取得、課題の確認、ファイルのダウンロード、小テスト結果の閲覧などをプログラムから行うことができます。

## 主な機能

*   **認証の自動化**: ログインフローを処理し、セッションを作成します。
*   **セッションの永続化**: セッション Cookie をローカルの JSON ファイルに保存し、再ログインの手間を省きます。
*   **コース管理**: 登録しているコースの一覧や、コースカテゴリを閲覧できます。
*   **コンテンツの抽出**:
    *   **課題 (Assignments)**: 提出期限、提出状況、添付ファイルへのリンクを取得します。
    *   **小テスト (Quizzes)**: 受験履歴、評点、フィードバックを確認できます。
    *   **リソース**: ファイルやフォルダの直接ダウンロード URL を解決します。
    *   **フォーラム & ページ**: コンテンツや概要を抽出します。
*   **ファイルダウンロード**: コース資料や提出ファイルをダウンロードします。

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

### 基本的な使い方

```python
from pymoodle.client import MoodleClient
import getpass

# クライアントの初期化
client = MoodleClient(
    base_url="https://moodle.example.com/",
    session_file="moodle_session.json"
)

# ログイン（セッションが保存されていない、または期限切れの場合）
if not client.load_session() or not client.is_logged_in():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    if client.login(username, password):
        print("ログイン成功")
    else:
        print("ログイン失敗")
        exit()

# 受講コースの取得
courses = client.get_my_courses()
for course in courses:
    print(f"{course.name} (ID: {course.id})")

# コースコンテンツの取得
course_id = 12345
sections = client.get_course_contents(course_id)
for section in sections:
    print(f"セクション: {section.name}")
    for module in section.modules:
        print(f"  - {module.name} ({module.type})")
```

### クイズの自動化

PyMoodle はクイズの詳細取得、受験開始、回答の送信をサポートしています。

```python
# クイズ詳細の取得
quiz_id = 99999
details = client.get_quiz_details(quiz_id)

if details.can_attempt:
    # 新しい受験を開始
    attempt_url = client.start_quiz_attempt(details.cmid, details.sesskey)

    # 受験データ（問題）の取得
    attempt_data = client.get_quiz_attempt_data(attempt_url)

    # 回答の準備
    # inputのname属性と値をマッピングします
    answers = {
        'q123:1_answer': '1',           # 選択肢の値
        'q123:2_answer': 'My Answer',   # テキスト入力
    }

    # 回答の送信（保存）
    client.submit_quiz_answers(attempt_data, answers)

    # 受験の終了（すべて送信して終了）
    client.finish_quiz_attempt(attempt_data.attempt_id, attempt_data.sesskey, str(details.cmid))
```

### データモデル

すべての API メソッドは、辞書ではなく **Dataclass** オブジェクトを返すようになり、IDE の補完や型安全性が向上しました。

- `Course`
- `Category`
- `Section`
- `Module`
- `QuizDetails`
- `QuizAttemptData`
- `QuizQuestion`
- その他 `pymoodle.types` に定義されています。

## サンプル

`examples/` ディレクトリに完全なスクリプトがあります：

- `list_courses.py`: 受講コースの一覧を表示します。
- `get_course_contents.py`: 特定のコースのコンテンツを表示します。
- `download_resource.py`: ファイルリソースをダウンロードします。
- `quiz_attempt.py`: クイズを取得して回答するデモです。

## API リファレンス

### `MoodleClient`

**初期化・認証**
- `__init__(base_url, session_file="session.json")`: クライアントを初期化します。
- `login(username, password) -> bool`: ユーザー名とパスワードでログインします。
- `load_session() -> bool`: 保存されたセッションファイルを読み込みます。
- `is_logged_in() -> bool`: 現在のセッションが有効（ログイン済み）か確認します。

**コース・カテゴリ**
- `get_my_courses() -> List[Course]`: 登録されているコースの一覧を取得します。
- `get_course_contents(course_id) -> List[Section]`: 指定したコースのセクションとモジュール構成を取得します。
- `get_course_categories(category_id=None) -> List[Category]`: コースカテゴリの一覧を取得します。

**モジュール詳細**
- `get_quiz_details(quiz_id) -> Optional[QuizDetails]`: クイズ（小テスト）の詳細を取得します。
- `get_assignment_details(assign_id) -> Optional[Dict]`: 課題の詳細を取得します。
- `get_folder_details(folder_id) -> Optional[Dict]`: フォルダ内のファイル一覧を取得します。
- `get_page_details(page_id) -> Optional[Dict]`: ページモジュールの内容を取得します。
- `get_forum_details(forum_id) -> Optional[Dict]`: フォーラムの概要を取得します。
- `get_resource_download_url(resource_id) -> Optional[str]`: リソースファイルのダウンロードURLを取得します。
- `get_external_url(url_id) -> Optional[str]`: 外部リンクのURLを取得します。

**クイズ操作**
- `start_quiz_attempt(cmid, sesskey) -> Optional[str]`: クイズの受験を開始し、受験ページのURLを返します。
- `get_quiz_attempt_data(attempt_url) -> Optional[QuizAttemptData]`: 受験ページから問題データを解析して取得します。
- `submit_quiz_answers(attempt_data, answers, finish_attempt=False) -> Optional[str]`: 回答を送信します。`finish_attempt=True` で「テストを終了する」ボタンを押した挙動になります。
- `finish_quiz_attempt(attempt_id, sesskey, cmid) -> Optional[str]`: 概要ページから「すべて送信して終了する」を実行します。

**ユーティリティ**
- `download_file(url, save_dir) -> Optional[str]`: 指定したURLからファイルをダウンロードして保存します。

## エラーハンドリング

`pymoodle.exceptions` で定義されている例外：

- `MoodleError`: ベース例外クラス。
- `MoodleLoginError`: ログイン失敗時に発生します。
- `MoodleRequestError`: HTTPリクエスト失敗時に発生します。
- `MoodleParseError`: HTML解析失敗時に発生します。

```python
from pymoodle.exceptions import MoodleLoginError

try:
    client.login(user, pwd)
except MoodleLoginError as e:
    print(f"認証エラー: {e}")
```

## 免責事項

このライブラリは **非公式** であり、Moodle HQ とは提携していません。Web スクレイピングに依存しているため、以下の点に注意してください：
1. Moodle のテーマや DOM 構造が大幅に変更された場合、**動作しなくなる可能性**があります。
2. **全て自己責任でお願いします。**

## ライセンス

[MIT License](LICENSE)
