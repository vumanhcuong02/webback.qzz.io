#!/usr/bin/env python3
"""
AI Agent tự động viết bài cho Ninh Hòa Blog
- Gọi NVIDIA NIM API để sinh nội dung
- Hỗ trợ Tiếng Việt và English
- Tạo file HTML + cập nhật posts.json
- Push lên GitHub
"""

import os
import json
import random
import subprocess
import re
import html
from datetime import datetime

# === CẤU HÌNH ===
GITHUB_REPO = "https://github.com/vumanhcuong02/webback.qzz.io.git"
LOCAL_DIR = "/home/opc/webback"
NVIDIA_API_KEY = "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"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "deepseek-ai/deepseek-v4-pro"

# Danh sách chủ đề linh hoạt
TOPICS_VI = [
    # AI Tools & So sánh
    "So sánh ChatGPT và Claude: Nên dùng công cụ nào?",
    "Top 10 công cụ AI miễn phí tốt nhất hiện nay",
    "Gemini vs ChatGPT: Đâu là trợ lý AI toàn diện hơn?",
    "Cách dùng AI để tăng năng suất làm việc gấp đôi",
    "Review Cursor AI: Công cụ lập trình AI tốt nhất 2025?",
    "So sánh GitHub Copilot và Cursor: IDE AI nào mạnh hơn?",
    "Top AI tool viết content tốt nhất cho Blogger",
    "Perplexity AI vs ChatGPT: Công cụ tìm kiếm nào tốt hơn?",
    "Hướng dẫn dùng Claude AI để viết code hiệu quả",
    "Midjourney vs DALL-E vs Stable Diffusion: AI vẽ ảnh nào đỉnh nhất?",

    # Hướng dẫn AI
    "Prompt Engineering cơ bản: Cách gõ lệnh cho AI hiểu đúng ý bạn",
    "Hướng dẫn dùng ChatGPT từ A-Z cho người mới bắt đầu",
    "Cách viết email chuyên nghiệp với AI trong 1 phút",
    "Hướng dẫn tạo ảnh AI đẹp với prompt chuẩn",
    "Cách dùng AI để học lập trình nhanh hơn",
    "AI có thể thay thế lập trình viên không?",
    "Hướng dẫn tạo chatbot AI đơn giản không cần code",

    # Tin tức & Xu hướng
    "Những xu hướng AI đáng chú ý nhất năm 2025",
    "AI trong giáo dục: Cách mạng hóa việc học tập",
    "Tương lai việc làm trong thời đại AI",
    "AI và dữ liệu lớn: Bộ đôi thay đổi thế giới",
    "Những rủi ro khi dùng AI và cách phòng tránh",
    "AI trong y tế: Những đột phá mới nhất",
    "Trí tuệ nhân tạo đang thay đổi ngành marketing như thế nào?",

    # Thủ thuật & Kinh nghiệm
    "5 thói quen giúp bạn tận dụng AI hiệu quả mỗi ngày",
    "Cách kiếm tiền với AI cho người mới bắt đầu",
    "Sai lầm thường gặp khi dùng AI và cách khắc phục",
    "10 câu lệnh prompt hay nhất cho dân văn phòng",
    "Cách dùng AI để phân tích dữ liệu nhanh chóng",
    "Ứng dụng AI trong kinh doanh online",
    "Học machine learning cơ bản với AI hỗ trợ",

    # Review sản phẩm
    "Review ChatGPT Plus: Có đáng để đầu tư?",
    "Trải nghiệm Claude Pro: Có nên nâng cấp?",
    "Gemini Advanced: Google có làm nên chuyện?",
    "So sánh Notion AI và các công cụ ghi chú AI khác",
    "Review các extension AI cho Chrome hữu ích nhất",
    "Top ứng dụng AI trên điện thoại bạn nên dùng thử",
]

TOPICS_EN = [
    "ChatGPT vs Claude: Which AI Assistant Should You Choose?",
    "Top 10 Free AI Tools You Need to Try in 2025",
    "Gemini vs ChatGPT: A Comprehensive Comparison",
    "How to Double Your Productivity with AI in 2025",
    "Cursor AI Review: The Best AI Code Editor?",
    "GitHub Copilot vs Cursor: Which AI Coding Tool Wins?",
    "Best AI Writing Tools for Bloggers and Content Creators",
    "Perplexity AI vs ChatGPT: Which Search Tool is Better?",
    "How to Use Claude AI for Efficient Coding",
    "Midjourney vs DALL-E vs Stable Diffusion: AI Art Comparison",

    "Prompt Engineering Basics: Getting AI to Understand You",
    "ChatGPT Guide for Beginners: From Zero to Hero",
    "How to Write Professional Emails with AI in 1 Minute",
    "AI Image Generation Guide: Mastering Prompts",
    "How to Learn Programming Faster with AI",
    "Will AI Replace Software Developers?",
    "How to Build a Simple AI Chatbot Without Code",

    "Top AI Trends to Watch in 2025",
    "AI in Education: Revolutionizing Learning",
    "The Future of Work in the Age of AI",
    "Big Data and AI: A Powerful Combination",
    "AI Risks and How to Avoid Them",
    "AI in Healthcare: Latest Breakthroughs",
    "How AI is Transforming Digital Marketing",

    "5 Daily Habits to Make the Most of AI",
    "How to Make Money with AI as a Beginner",
    "Common AI Mistakes and How to Fix Them",
    "10 Best Prompts for Office Workers",
    "How to Analyze Data Quickly with AI",
    "AI Applications in E-commerce and Online Business",
    "Learn Machine Learning Basics with AI Assistance",

    "ChatGPT Plus Review: Is It Worth It?",
    "Claude Pro Experience: Should You Upgrade?",
    "Gemini Advanced: Can Google Deliver?",
    "Notion AI vs Other AI Note-Taking Tools",
    "Best AI Chrome Extensions You Should Install",
    "Top AI Mobile Apps Worth Trying in 2025",
]

TAGS_VI = ["So sánh AI", "Hướng dẫn AI", "Tin tức AI", "Thủ thuật AI", "Review AI"]
TAGS_EN = ["AI Comparison", "AI Tutorial", "AI News", "AI Tips", "AI Review"]

def call_nvidia(prompt, lang="vi"):
    """Gọi NVIDIA NIM API để sinh nội dung"""
    system_prompt = (
        "Bạn là một blogger công nghệ chuyên nghiệp. "
        "Viết bài blog chi tiết, dễ hiểu, giọng văn tự nhiên, chuẩn SEO. "
        "Độ dài: 800-1500 từ. Có tiêu đề (h2, h3), in đậm những ý chính, "
        "dùng bullet points, highlight box cho kết luận quan trọng." if lang == "vi" else
        "You are a professional tech blogger. "
        "Write detailed, easy-to-understand blog posts with natural tone, SEO-optimized. "
        "Length: 800-1500 words. Use headings (h2, h3), bold for key points, "
        "bullet points, highlight boxes for important conclusions."
    )

    full_prompt = f"{system_prompt}\n\nChủ đề: {prompt}\n\nHãy viết bài blog hoàn chỉnh."

    data = {
        "model": NVIDIA_MODEL,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": 0.8,
        "max_tokens": 3000,
        "top_p": 0.95
    }

    cmd = [
        "curl", "-s", NVIDIA_URL,
        "-H", f"Authorization: Bearer {NVIDIA_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        out = result.stdout.decode('utf-8')
        resp = json.loads(out)
        content = resp["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        print(f"Lỗi gọi API: {e}")
        return None

def extract_title(content, topic):
    """Trích xuất tiêu đề từ nội dung"""
    lines = content.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line.startswith('#'):
            return line.lstrip('#').strip()
    return topic

def html_to_plain_text(html_text):
    """Loại bỏ HTML tags và markdown để lấy mô tả"""
    text = re.sub(r'<[^>]+>', '', html_text)
    text = re.sub(r'#{1,6}\s?', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def create_html_article(content, title, tag, date_str, slug, lang="vi"):
    """Tạo file HTML từ nội dung"""
    # Chuẩn bị meta
    if lang == "vi":
        site_title = "Ninh Hòa Blog - Công Nghệ & AI"
        lang_code = "vi"
        back_text = "← Về trang chủ"
        og_locale = "vi_VN"
    else:
        site_title = "Ninh Hoa Blog - Technology & AI"
        lang_code = "en"
        back_text = "← Back to home"
        og_locale = "en_US"

    # Xử lý nội dung (markdown to HTML đơn giản)
    body = html.escape(content)
    body = content  # keep original markdown for now

    # Chuyển markdown cơ bản sang HTML
    lines = body.split('\n')
    html_lines = []
    in_list = False
    for line in lines:
        # Headers
        if line.startswith('### '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h2>{line[2:]}</h2>')
        # Bold/italic
        elif '**' in line:
            if in_list: html_lines.append('</ul>'); in_list = False
            line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
            # Highlight box
            if 'Kết luận' in line or 'Tóm lại' in line or 'Conclusion' in line or 'Summary' in line:
                html_lines.append(f'<div class="highlight">{line}</div>')
            else:
                html_lines.append(f'<p>{line}</p>')
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        elif line.startswith('1. ') or line.startswith('2. '):
            if not in_list:
                html_lines.append('<ol>')
                in_list = True
            html_lines.append(f'<li>{line[3:]}</li>')
        elif line.strip() == '':
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('')
        else:
            if in_list: html_lines.append('</ul>'); in_list = False
            # Check for highlight box
            if 'Kết luận' in line or 'Tóm lại' in line or 'Tổng kết' in line or 'Conclusion' in line or 'Summary' in line:
                html_lines.append(f'<div class="highlight">{line}</div>')
            else:
                html_lines.append(f'<p>{line}</p>')
    if in_list:
        html_lines.append('</ul>')

    body_html = '\n'.join(html_lines)

    description = html_to_plain_text(content)[:160]

    if lang == "vi":
        canonical = f"https://webback.qzz.io/{slug}.html"
    else:
        canonical = f"https://webback.qzz.io/en/{slug}.html"

    html_template = f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {site_title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:locale" content="{og_locale}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.8; }}
        .article-header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f3460 100%); color: white; padding: 24px 20px; text-align: center; }}
        .article-header a {{ color: #38bdf8; text-decoration: none; font-weight: 500; }}
        .container {{ max-width: 750px; margin: 40px auto 60px; padding: 0 20px; }}
        .article {{ background: white; border-radius: 20px; padding: 45px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .article h1 {{ font-size: 2em; margin-bottom: 10px; line-height: 1.3; }}
        .article .meta {{ display: flex; gap: 16px; color: #64748b; font-size: 0.9em; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #f1f5f9; }}
        .article .meta i {{ margin-right: 4px; }}
        .article p {{ margin-bottom: 18px; color: #475569; }}
        .article h2 {{ font-size: 1.4em; margin: 35px 0 15px; color: #0f172a; }}
        .article h3 {{ font-size: 1.15em; margin: 25px 0 12px; color: #1e293b; }}
        .article ul, .article ol {{ margin: 0 0 18px 24px; color: #475569; }}
        .article li {{ margin-bottom: 8px; }}
        .article strong {{ color: #0f172a; }}
        .article .highlight {{ background: #eef2ff; border-left: 4px solid #4338ca; padding: 18px 22px; border-radius: 0 10px 10px 0; margin: 25px 0; color: #1e293b; font-weight: 500; }}
        .article a {{ color: #2563eb; }}
        .footer {{ text-align: center; padding: 30px; color: #94a3b8; font-size: 0.85em; }}
        .lang-switch {{ display: inline-block; background: #eef2ff; color: #4338ca; padding: 6px 16px; border-radius: 8px; text-decoration: none; font-size: 0.85em; font-weight: 500; margin-top: 10px; }}
        @media (max-width: 600px) {{ .article {{ padding: 24px; }} .article h1 {{ font-size: 1.4em; }} }}
    </style>
</head>
<body>
    <div class="article-header">
        <p><a href="/{'en' if lang == 'en' else ''}">{back_text}</a></p>
        <a class="lang-switch" href="/{'en/' if lang == 'vi' else ''}{slug}.html">
            <i class="fas fa-globe"></i> {'English' if lang == 'vi' else 'Tiếng Việt'}
        </a>
    </div>
    <div class="container">
        <div class="article">
            <h1>{title}</h1>
            <div class="meta">
                <span><i class="far fa-calendar"></i> {date_str}</span>
                <span><i class="fas fa-tag"></i> {tag}</span>
                <span><i class="far fa-clock"></i> {(len(content)//1000)+1} phút đọc</span>
            </div>
            {body_html}
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2025 Ninh Hòa Blog. {'Tự động vận hành bởi AI.' if lang == 'vi' else 'Powered by AI.'}</p>
        <p><a href="/{'en/' if lang == 'en' else ''}" style="color:#2563eb;">{'← Về trang chủ' if lang == 'vi' else '← Back to home'}</a></p>
    </div>
</body>
</html>"""

    return html_template


def slugify(text):
    """Tạo slug từ tiêu đề"""
    text = text.lower()
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'đ', 'd', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text.strip())
    text = text[:80].strip('-')
    return text


def update_posts_json(slug, title, tag, date_str, description, lang="vi"):
    """Cập nhật posts.json"""
    # Xác định file
    if lang == "en":
        json_path = os.path.join(LOCAL_DIR, "en", "posts.json")
    else:
        json_path = os.path.join(LOCAL_DIR, "posts.json")

    # Đọc posts.json hiện tại
    posts = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except:
            posts = []

    # Thêm bài mới
    new_post = {
        "title": title,
        "slug": slug,
        "tag": tag,
        "date": date_str,
        "description": description[:200]
    }

    # Kiểm tra trùng
    if not any(p['slug'] == slug for p in posts):
        posts.insert(0, new_post)

    # Ghi lại
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    return posts


def update_index_html(posts, lang="vi"):
    """Cập nhật index.html với danh sách bài viết mới nhất"""
    pass  # index.html đã dùng JavaScript để load từ posts.json


def git_push():
    """Push code lên GitHub"""
    try:
        os.chdir(LOCAL_DIR)
        subprocess.run(["git", "add", "."], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "commit", "-m", f"AI agent: Them bai viet {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "push"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Push thành công lên GitHub")
        return True
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode('utf-8') if e.stderr else 'nothing to commit'
        print(f"⚠️ Git push: {err}")
        return False


def write_article(content, title, tag, date_str, slug, lang="vi"):
    """Ghi file HTML bài viết"""
    html_content = create_html_article(content, title, tag, date_str, slug, lang)

    if lang == "en":
        dir_path = os.path.join(LOCAL_DIR, "en")
    else:
        dir_path = LOCAL_DIR

    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{slug}.html")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Đã viết bài: {file_path}")
    return file_path


def main():
    """Main - chọn chủ đề, gọi API, viết bài, push"""
    print("="*50)
    print(f"🤖 AI Agent - Bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Clone/pull repo
    if not os.path.exists(LOCAL_DIR):
        subprocess.run(["git", "clone", GITHUB_REPO, LOCAL_DIR], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        os.chdir(LOCAL_DIR)
        subprocess.run(["git", "pull"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Chọn ngẫu nhiên chủ đề
    lang = random.choices(["vi", "en"], weights=[2, 1])[0]  # ưu tiên tiếng Việt

    if lang == "vi":
        topic = random.choice(TOPICS_VI)
        tag = random.choice(TAGS_VI)
    else:
        topic = random.choice(TOPICS_EN)
        tag = random.choice(TAGS_EN)

    print(f"📝 Chủ đề ({lang}): {topic}")

    # Gọi API
    content = call_nvidia(topic, lang)
    if not content:
        print("❌ Lỗi: Không lấy được nội dung từ API")
        return

    # Tạo slug và metadata
    title = extract_title(content, topic)
    slug = slugify(title)
    date_str = datetime.now().strftime("%Y-%m-%d")
    description = html_to_plain_text(content)[:200]

    print(f"📄 Tiêu đề: {title}")
    print(f"🔗 Slug: {slug}")

    # Viết file HTML
    write_article(content, title, tag, date_str, slug, lang)

    # Cập nhật posts.json
    posts = update_posts_json(slug, title, tag, date_str, description, lang)

    # Push lên GitHub
    git_push()

    print(f"✅ Hoàn thành: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)


if __name__ == "__main__":
    main()