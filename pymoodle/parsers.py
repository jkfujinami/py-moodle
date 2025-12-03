from bs4 import BeautifulSoup
from typing import List, Optional
from pymoodle.types import Course, Category, Section, Module, FileItem, FolderDetails, AssignmentDetails, ForumDetails, PageDetails, QuizDetails, QuizAttempt, QuizQuestion, QuizAttemptData

def parse_my_courses(html: str) -> List[Course]:
    soup = BeautifulSoup(html, 'html.parser')
    courses: List[Course] = []

    course_items = soup.select('.coursebox')
    if not course_items:
        course_items = soup.select('div[data-region="course-content"]')

    if not course_items:
         nav_links = soup.select('nav .list-group-item[href*="course/view.php"]')
         for link in nav_links:
             href = link.get('href')
             name = link.get_text(strip=True)
             if 'id=' in href:
                 try:
                     course_id = int(href.split('id=')[1].split('&')[0])
                     courses.append(Course(
                         id=course_id,
                         name=name,
                         url=href,
                         image_url=None,
                         teachers=[]
                     ))
                 except ValueError:
                     pass
         seen_ids = set()
         unique_courses = []
         for c in courses:
             if c.id not in seen_ids:
                 unique_courses.append(c)
                 seen_ids.add(c.id)
         return unique_courses

    for item in course_items:
        course_id_str = item.get('data-courseid')

        name_tag = item.select_one('.coursename a')
        if not name_tag:
            link_tag = item.find('a', href=True)
            if not link_tag: continue
            url = link_tag['href']
            name = item.get_text(strip=True)
        else:
            url = name_tag['href']
            name = name_tag.get_text(strip=True)

        if not course_id_str:
            from urllib.parse import parse_qs, urlparse
            try:
                parsed_url = urlparse(url)
                qs = parse_qs(parsed_url.query)
                course_id = int(qs['id'][0])
            except (ValueError, KeyError, IndexError):
                continue
        else:
            course_id = int(course_id_str)

        image_url = None
        img_div = item.select_one('.card-img-top') or item.select_one('.course-image')
        if img_div:
            import re
            style = img_div.get('style', '')
            if 'url(' in style:
                match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                if match:
                    image_url = match.group(1)
            else:
                img_tag = img_div.find('img')
                if img_tag:
                    image_url = img_tag.get('src')

        teachers = []
        teacher_links = item.select('.teachers li a')
        for t_link in teacher_links:
            teachers.append(t_link.get_text(strip=True))

        courses.append(Course(
            id=course_id,
            name=name,
            url=url,
            image_url=image_url,
            teachers=teachers
        ))

    return courses

def parse_course_contents(html: str) -> List[Section]:
    soup = BeautifulSoup(html, 'html.parser')
    sections: List[Section] = []

    topic_list = soup.select('ul.topics li.section.main')
    if not topic_list:
         topic_list = soup.select('.course-content ul.topics li.section.main') or \
                      soup.select('.course-content ul.weeks li.section.main')

    for section in topic_list:
        section_id = section.get('data-sectionid')

        name_tag = section.select_one('.sectionname')
        if name_tag:
            section_name = name_tag.get_text(strip=True)
        else:
            section_name = f"Section {section_id}"

        summary_tag = section.select_one('.summary')
        section_summary = summary_tag.get_text(strip=True) if summary_tag else ""

        modules: List[Module] = []
        module_items = section.select('ul.section li.activity')

        for mod in module_items:
            mod_id_str = mod.get('id')
            mod_id = int(mod_id_str.replace('module-', '')) if mod_id_str else None

            classes = mod.get('class', [])
            mod_type = "unknown"
            for c in classes:
                if c.startswith('modtype_'):
                    mod_type = c.replace('modtype_', '')
                    break

            instancename_tag = mod.select_one('.instancename')
            link_tag = mod.select_one('.activityinstance a')

            if instancename_tag:
                for hidden in instancename_tag.select('.accesshide'):
                    hidden.decompose()
                mod_name = instancename_tag.get_text(strip=True)
            else:
                mod_name = "Untitled"

            mod_url = link_tag['href'] if link_tag else None

            description = None
            desc_tag = mod.select_one('.contentafterlink')
            if desc_tag:
                description = desc_tag.get_text(separator="\n", strip=True)

            is_completed = False
            completion_icon = mod.select_one('.autocompletion img')
            if completion_icon:
                title = completion_icon.get('title', '') or completion_icon.get('alt', '')
                if "完了: " in title and "未完了" not in title:
                    is_completed = True

            modules.append(Module(
                id=mod_id,
                type=mod_type,
                name=mod_name,
                url=mod_url,
                description=description,
                completed=is_completed
            ))

        sections.append(Section(
            id=section_id,
            name=section_name,
            summary=section_summary,
            modules=modules
        ))

    return sections

def parse_categories(html: str, is_subcategory: bool = False) -> List[Category]:
    soup = BeautifulSoup(html, 'html.parser')
    categories: List[Category] = []

    if is_subcategory:
        container = soup.select_one('.subcategories')
        if container:
            category_items = container.select('.category')
        else:
            category_items = soup.select('.category')
    else:
        category_items = soup.select('.category')

    for item in category_items:
        cat_id = item.get('data-categoryid')

        name_tag = item.select_one('.categoryname a')
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)
        url = name_tag['href']

        count_span = item.select_one('.numberofcourse')
        course_count = 0
        if count_span:
            import re
            match = re.search(r'\((\d+)\)', count_span.get_text())
            if match:
                course_count = int(match.group(1))

        categories.append(Category(
            id=int(cat_id) if cat_id else None,
            name=name,
            url=url,
            course_count=course_count,
            has_children="with_children" in item.get("class", [])
        ))

    return categories

def parse_resource_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, 'html.parser')

    content_div = soup.select_one('.resourcecontent')
    if content_div:
        link = content_div.find('a', href=True)
        if link:
            return link['href']

    iframe = soup.select_one('iframe.resourceembed')
    if iframe:
        return iframe['src']

    obj_tag = soup.select_one('object.resourceembed')
    if obj_tag:
        return obj_tag['data']

    workaround = soup.select_one('.resourceworkaround a')
    if workaround:
        return workaround['href']

    return None

def parse_external_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, 'html.parser')
    return None

def _parse_file_tree(container) -> List[FileItem]:
    """
    Moodleのファイルツリー構造からファイルリストを抽出するヘルパー関数
    """
    files: List[FileItem] = []
    if not container:
        return files

    # ファイルリンクを探す
    # <span class="fp-filename-icon"><a href="...">...</a></span>
    for link in container.select('.fp-filename-icon a'):
        href = link.get('href')
        # ?forcedownload=1 を除去するかどうかは要検討だが、そのまま保持しておく

        filename_span = link.select_one('.fp-filename')
        filename = filename_span.get_text(strip=True) if filename_span else link.get_text(strip=True)

        # アイコンからMIMEタイプを推測（簡易）
        mimetype = None
        img = link.select_one('img.icon')
        if img:
            src = img.get('src', '')
            if '/pdf' in src: mimetype = 'application/pdf'
            elif '/document' in src: mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif '/archive' in src: mimetype = 'application/zip'

        files.append(FileItem(
            filename=filename,
            url=href,
            mimetype=mimetype
        ))
    return files

def parse_folder(html: str) -> FolderDetails:
    soup = BeautifulSoup(html, 'html.parser')

    title = ""
    h2 = soup.select_one('h2')
    if h2:
        title = h2.get_text(strip=True)

    # ファイルツリー
    tree_container = soup.select_one('.foldertree')
    files = _parse_file_tree(tree_container)

    # 一括ダウンロードボタン
    download_all_url = None
    form = soup.select_one('form[action*="download_folder.php"]')
    if form:
        # formのaction属性そのものではなく、ボタンを押したときの挙動だが、
        # 通常はPOSTでIDを送る。GETでアクセスできるリンクがあるか？
        # Moodleの仕様では download_folder.php?id=XXX でDLできることが多い
        action = form.get('action')
        id_input = form.select_one('input[name="id"]')
        if action and id_input:
            download_all_url = f"{action}?id={id_input.get('value')}"

    return FolderDetails(
        title=title,
        files=files,
        download_all_url=download_all_url
    )

def parse_assignment(html: str) -> AssignmentDetails:
    soup = BeautifulSoup(html, 'html.parser')

    title = ""
    h2 = soup.select_one('div[role="main"] h2')
    if h2:
        title = h2.get_text(strip=True)

    intro_div = soup.select_one('#intro')
    intro = intro_div.get_text(separator="\n", strip=True) if intro_div else ""

    # 添付ファイル (introの直後にあるファイルツリー)
    attachments: List[FileItem] = []
    if intro_div:
        # intro_divの次の要素を探す
        next_el = intro_div.find_next_sibling('div', id=lambda x: x and x.startswith('assign_files_tree'))
        if next_el:
            attachments = _parse_file_tree(next_el)

    # ステータステーブル
    status_table = soup.select_one('.submissionstatustable table.generaltable')
    submission_status = ""
    grading_status = ""
    due_date = ""
    time_remaining = ""
    last_modified = ""
    submission_files: List[FileItem] = []

    if status_table:
        rows = status_table.select('tr')
        for row in rows:
            th = row.select_one('th')
            td = row.select_one('td')
            if not th or not td: continue

            header = th.get_text(strip=True)
            value = td.get_text(strip=True)

            if "提出ステータス" in header:
                submission_status = value
            elif "評定ステータス" in header:
                grading_status = value
            elif "終了日時" in header:
                due_date = value
            elif "残り時間" in header:
                time_remaining = value
            elif "最終更新日時" in header:
                last_modified = value
            elif "ファイル提出" in header:
                # ファイル提出セル内のツリー
                submission_files = _parse_file_tree(td)

    return AssignmentDetails(
        title=title,
        intro=intro,
        attachments=attachments,
        submission_status=submission_status,
        grading_status=grading_status,
        due_date=due_date,
        time_remaining=time_remaining,
        last_modified=last_modified,
        submission_files=submission_files
    )

def parse_forum(html: str) -> ForumDetails:
    soup = BeautifulSoup(html, 'html.parser')

    title = ""
    h2 = soup.select_one('div[role="main"] h2')
    if h2:
        title = h2.get_text(strip=True)

    intro_div = soup.select_one('#intro')
    intro = intro_div.get_text(separator="\n", strip=True) if intro_div else ""

    has_discussions = True
    if soup.select_one('.forumnodiscuss'):
        has_discussions = False

    return ForumDetails(
        title=title,
        intro=intro,
        has_discussions=has_discussions
    )

def parse_page(html: str) -> PageDetails:
    soup = BeautifulSoup(html, 'html.parser')

    title = ""
    h2 = soup.select_one('div[role="main"] h2')
    if h2:
        title = h2.get_text(strip=True)

    content = ""
    generalbox = soup.select_one('.generalbox')
    if generalbox:
        # コンテンツ内の不要な要素を除去する場合があればここで処理
        content = generalbox.decode_contents()

    last_modified = ""
    modified_div = soup.select_one('.modified')
    if modified_div:
        last_modified = modified_div.get_text(strip=True).replace("最終更新日時:", "").strip()

    return PageDetails(
        title=title,
        content=content,
        last_modified=last_modified
    )

def parse_quiz(html: str) -> QuizDetails:
    soup = BeautifulSoup(html, 'html.parser')

    title = ""
    h2 = soup.select_one('div[role="main"] h2')
    if h2:
        title = h2.get_text(strip=True)

    intro_div = soup.select_one('#intro')
    if not intro_div:
        intro_div = soup.select_one('.quizinfo')
    intro = intro_div.get_text(separator="\n", strip=True) if intro_div else ""

    attempts: List[QuizAttempt] = []
    summary_table = soup.select_one('.quizattemptsummary')
    if summary_table:
        # ヘッダーから列インデックスを特定
        headers = [th.get_text(strip=True) for th in summary_table.select('thead th')]

        grade_idx = -1
        review_idx = -1
        feedback_idx = -1

        for i, h in enumerate(headers):
            if "評点" in h or "素点" in h or "Grade" in h or "Marks" in h:
                # 評点列が複数ある場合（素点と評点など）、最後のものを採用するか、
                # "評点 /" を優先するなどのロジックが必要。
                # ここでは単純に「評点」を含む最後の列をgradeとする（素点があっても評点が重要）
                grade_idx = i
            elif "レビュー" in h or "Review" in h:
                review_idx = i
            elif "フィードバック" in h or "Feedback" in h:
                feedback_idx = i

        rows = summary_table.select('tbody tr')
        for row in rows:
            cells = row.select('td')
            if not cells: continue

            try:
                attempt_num = int(cells[0].get_text(strip=True))
            except (ValueError, IndexError):
                continue

            state = cells[1].get_text(separator=" ", strip=True) if len(cells) > 1 else ""

            grade = None
            if grade_idx != -1 and len(cells) > grade_idx:
                grade = cells[grade_idx].get_text(strip=True)

            review_url = None
            # レビュー列があればそこから、なければ行全体から探す
            if review_idx != -1 and len(cells) > review_idx:
                link = cells[review_idx].find('a', href=True)
                if link: review_url = link['href']

            if not review_url:
                link = row.find('a', href=True)
                if link and 'review.php' in link['href']:
                    review_url = link['href']

            feedback = None
            if feedback_idx != -1 and len(cells) > feedback_idx:
                feedback = cells[feedback_idx].get_text(strip=True)

            attempts.append(QuizAttempt(
                attempt_number=attempt_num,
                state=state,
                grade=grade,
                review_url=review_url,
                feedback=feedback
            ))

    feedback_div = soup.select_one('#feedback')
    overall_feedback = feedback_div.get_text(separator="\n", strip=True) if feedback_div else None

    can_attempt = False
    cmid = None
    sesskey = None

    start_form = soup.select_one('form[action*="startattempt.php"]')
    if start_form:
        can_attempt = True
        cmid_input = start_form.select_one('input[name="cmid"]')
        if cmid_input:
            try:
                cmid = int(cmid_input.get('value'))
            except (ValueError, TypeError):
                pass

        sesskey_input = start_form.select_one('input[name="sesskey"]')
        if sesskey_input:
            sesskey = sesskey_input.get('value')

    return QuizDetails(
        title=title,
        intro=intro,
        attempts=attempts,
        feedback=overall_feedback,
        can_attempt=can_attempt,
        cmid=cmid,
        sesskey=sesskey,
        latest_attempt_data=None
    )

def parse_quiz_attempt(html: str) -> Optional[QuizAttemptData]:
    soup = BeautifulSoup(html, 'html.parser')

    form = soup.select_one('#responseform')
    if not form:
        return None

    attempt_id = form.select_one('input[name="attempt"]')['value']
    sesskey = form.select_one('input[name="sesskey"]')['value']
    slots = form.select_one('input[name="slots"]')['value']

    questions: List[QuizQuestion] = []
    question_divs = form.select('.que')

    for q_div in question_divs:
        q_id = q_div.get('id') # e.g., question-566730-1

        # Extract question number
        q_no_tag = q_div.select_one('.qno')
        q_no = int(q_no_tag.get_text(strip=True)) if q_no_tag else 0

        # Extract question text (ignoring accesshide)
        content_div = q_div.select_one('.content')
        q_text = ""
        subquestions = []

        if content_div:
            # Remove accesshide elements temporarily to get clean text
            for hidden in content_div.select('.accesshide'):
                hidden.extract()

            formulation = content_div.select_one('.formulation')
            if formulation:
                # Handle multianswer (cloze) subquestions by replacing them with placeholders
                # and extracting their data simultaneously

                # We need to find subquestions in order of appearance in the text
                # Moodle usually puts them in .subquestion spans or directly as inputs/selects

                # Find all subquestion elements (selects or inputs) within formulation
                # We iterate through all descendants to find inputs/selects that are part of the question
                # Note: This is a bit complex because we want to replace them in the text AND parse them.

                # Strategy:
                # 1. Find all .subquestion elements or input/selects that look like answers.
                # 2. Parse them into our subquestions list.
                # 3. Replace the element in the DOM with a placeholder string.
                # 4. Get text from the modified DOM.

                sub_idx = 1

                # Cloze questions often wrap controls in span.subquestion, but not always.
                # We look for controls that have names like q123:4_sub5_answer

                # First, handle span.subquestion wrappers if they exist (common in Cloze)
                for sub_span in formulation.select('.subquestion'):
                    # Parse data
                    label_tag = sub_span.select_one('label')
                    # label might be hidden or empty

                    select = sub_span.select_one('select')
                    input_tag = sub_span.select_one('input')

                    control_name = ""
                    options = []
                    stype = "unknown"

                    if select:
                        stype = "select"
                        control_name = select.get('name')
                        for opt in select.select('option'):
                            val = opt.get('value')
                            text = opt.get_text(strip=True)
                            # Moodle sometimes uses value="0" for "Choose..." but also for valid answers.
                            # We should only exclude if value is empty OR text looks like a placeholder
                            if val is not None: # value="" is empty string, value=None is missing attribute
                                # Check for common placeholder text
                                if val == '0' and (text.startswith("選択") or text.startswith("Choose") or text == ""):
                                    continue
                                if val == "":
                                    continue
                                options.append({"value": val, "text": text})
                    elif input_tag:
                        stype = "text"
                        control_name = input_tag.get('name')

                    subquestions.append({
                        "label": f"Blank {sub_idx}",
                        "name": control_name,
                        "options": options,
                        "type": stype
                    })

                    # Replace with placeholder
                    sub_span.replace_with(f" [BLANK_{sub_idx}] ")
                    sub_idx += 1

                # Sometimes controls are not in .subquestion spans (e.g. simple input fields)
                # If we still have inputs/selects in formulation that haven't been handled (because they weren't in .subquestion)
                # we should handle them. But be careful not to double count if we already replaced them.
                # Since we replaced .subquestion elements, their children are gone from formulation.

                # Now look for remaining inputs/selects that are question answers
                # Moodle question inputs usually have names starting with q\d+:\d+_
                import re
                remaining_controls = formulation.find_all(['input', 'select'])
                for control in remaining_controls:
                    name = control.get('name', '')
                    if not name or 'sequencecheck' in name: continue

                    # Check if it looks like a question answer field
                    if re.match(r'q\d+:\d+_', name):
                        stype = "text" if control.name == 'input' else "select"
                        options = []
                        if stype == "select":
                            for opt in control.select('option'):
                                val = opt.get('value')
                                text = opt.get_text(strip=True)
                                # Same logic as above
                                if val is not None:
                                    if val == '0' and (text.startswith("選択") or text.startswith("Choose") or text == ""):
                                        continue
                                    if val == "":
                                        continue
                                    options.append({"value": val, "text": text})

                        subquestions.append({
                            "label": f"Blank {sub_idx}",
                            "name": name,
                            "options": options,
                            "type": stype
                        })

                        control.replace_with(f" [BLANK_{sub_idx}] ")
                        sub_idx += 1

                q_text = formulation.get_text(separator="\n", strip=True)

        # Determine type (simplified as we might have modified the DOM, but classes are on q_div)
        classes = q_div.get('class', [])
        q_type = "unknown"
        for c in classes:
            if c != "que" and c != "deferredfeedback" and c != "notyetanswered":
                q_type = c
                break

        # Extract sequencecheck
        # It's usually an input type="hidden" inside the question div with name ending in :sequencecheck
        sequencecheck = None
        seq_input = q_div.find('input', attrs={'name': re.compile(r':sequencecheck$')})
        if seq_input:
            sequencecheck = seq_input.get('value')

        # If no subquestions found via the above method (e.g. not a Cloze question),
        # we might need to handle standard multichoice options if we want to list them.
        # But for now, the request was specifically about fixing the text/options mixing in Cloze.

        questions.append(QuizQuestion(
            id=q_id,
            number=q_no,
            text=q_text,
            type=q_type,
            options=None,
            subquestions=subquestions,
            sequencecheck=sequencecheck
        ))

    return QuizAttemptData(
        attempt_id=attempt_id,
        sesskey=sesskey,
        slots=slots,
        questions=questions,
        next_url=None # Logic to find next page URL if needed
    )
