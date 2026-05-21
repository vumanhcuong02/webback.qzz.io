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
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"

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
    import urllib.request
    import ssl

    system_prompt = (
        "Bạn là một blogger công nghệ người Việt Nam. VIẾT BÀI BLOG HOÀN TOÀN BẰNG TIẾNG VIỆT, giọng văn thân thiện như đang trò chuyện với người bạn, 800-1000 từ.\n\n"
        "QUY TẮC NGHIÊM NGẶT:\n"
        "1. KHÔNG bắt đầu bằng 'Trong bài viết này' hay 'Hôm nay chúng ta'\n"
        "2. Bắt đầu bằng một câu hỏi, số liệu thú vị, hoặc tình huống cụ thể\n"
        "3. Dùng h2 cho tiêu đề phụ, h3 cho mục nhỏ hơn, có ít nhất 3-4 h2 sections\n"
        "4. Dùng **text** để in đậm từ khóa quan trọng (tối đa 5-7 lần)\n"
        "5. Dùng - cho bullet points, mỗi list có 3-5 items\n"
        "6. Đặt highlight box (kết luận) cuối bài, bắt đầu bằng '💡'\n"
        "7. KHÔNG dùng dấu === hoặc --- làm divider\n"
        "8. KHÔNG dùng tiếng Anh trong nội dung (trừ tên công cụ như ChatGPT, Claude)\n"
        "9. Mỗi đoạn 2-4 câu, ngắn gọn\n"
        "10. Thêm một câu chốt hấp dẫn ở đầu bài\n"
        "11. Có ít nhất 4-5 paragraphs cho mỗi section chính\n\n"
        "CHỦ ĐỀ: " if lang == "vi" else
        "You are a friendly US tech blogger. Write COMPLETELY IN ENGLISH, 800-1000 words, conversational and engaging like talking to a friend.\n\n"
        "STRICT RULES:\n"
        "1. NEVER start with 'In this article' or 'Today we will'\n"
        "2. Start with a question, interesting fact, or specific scenario\n"
        "3. Use h2 for subtitles, h3 for sub-sections, at least 3-4 h2 sections\n"
        "4. Use **text** to bold key terms (max 5-7 times)\n"
        "5. Use - for bullet points, each list has 3-5 items\n"
        "6. End with highlight box starting with '💡'\n"
        "7. NO === or --- separators\n"
        "8. NEVER mix in Vietnamese\n"
        "9. Keep paragraphs 2-4 sentences short\n"
        "10. Add an engaging hook sentence at the start\n"
        "11. Have at least 4-5 paragraphs for each main section\n\n"
        "TOPIC: "
    )
    full_prompt = f"{system_prompt}{prompt}\n\nWrite a complete, in-depth blog post."

    payload = {
        "model": NVIDIA_MODEL,
        "messages": [{"role": "user", "content": full_prompt[:2000]}],
        "temperature": 0.8,
        "max_tokens": 2000,
        "top_p": 0.95
    }

    try:
        req = urllib.request.Request(
            NVIDIA_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=240, context=ctx) as resp:
            result = json.loads(resp.read())
            msg = result["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning_content") or ""
            if not content:
                print("API returned no content, skipping...")
                return None
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

def clean_content(content):
    """Clean content - remove markdown separators and fix common issues"""
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip markdown separators
        if re.match(r'^[=\-*]{3,}$', stripped):
            continue
        # Skip lines that are just HTML comment markers
        if stripped.startswith('<!--') and stripped.endswith('-->'):
            continue
        # If line has HTML tags, keep as-is but strip extra whitespace
        if '<' in stripped and '>' in stripped:
            cleaned.append(stripped)
        elif stripped:
            cleaned.append(stripped)
    return '\n'.join(cleaned)


def create_html_article(content, title, tag, date_str, slug, lang="vi"):
    """Tạo file HTML từ nội dung"""
    if lang == "vi":
        site_title = "Ninh Hòa Blog - Công Nghệ & AI"
        lang_code = "vi"
        back_text = "← Về trang chủ"
        og_locale = "vi_VN"
        home_link = "/"
        read_time = f"{(len(content)//1000)+1} phút đọc"
        footer_text = "Tự động vận hành bởi AI."
        share_text = "Chia sẻ bài viết"
        zalo_text = "Zalo"
        facebook_text = "Facebook"
        twitter_text = "Twitter"
    else:
        site_title = "Ninh Hoa Blog - Technology & AI"
        lang_code = "en"
        back_text = "← Back to home"
        og_locale = "en_US"
        home_link = "/en/"
        read_time = f"{(len(content)//1000)+1} min read"
        footer_text = "Powered by AI."
        share_text = "Share this article"
        zalo_text = "Zalo"
        facebook_text = "Facebook"
        twitter_text = "Twitter"

    body = clean_content(content).strip()

    # Check if content has HTML tags - if so, use as-is with minimal processing
    if '<' in body and '>' in body:
        # Content already has HTML, clean it up but don't escape
        # Remove any remaining markdown bold syntax that's not inside tags
        body_html = body
    else:
        # Pure markdown - convert to HTML
        lines = body.split('\n')
        html_lines = []
        in_list = False
        for line in lines:
            if line.startswith('### '):
                if in_list: html_lines.append('</ul>'); in_list = False
                html_lines.append(f'<h3>{html.escape(line[4:])}</h3>')
            elif line.startswith('## '):
                if in_list: html_lines.append('</ul>'); in_list = False
                html_lines.append(f'<h2>{html.escape(line[3:])}</h2>')
            elif line.startswith('# '):
                if in_list: html_lines.append('</ul>'); in_list = False
                html_lines.append(f'<h1>{html.escape(line[2:])}</h1>')
            elif '**' in line:
                if in_list: html_lines.append('</ul>'); in_list = False
                line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
                if 'Kết luận' in line or 'Tóm lại' in line or 'Conclusion' in line or 'Summary' in line:
                    html_lines.append(f'<div class="highlight">{line}</div>')
                else:
                    html_lines.append(f'<p>{line}</p>')
            elif line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{html.escape(line[2:])}</li>')
            elif line.startswith('1. ') or line.startswith('2. '):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                html_lines.append(f'<li>{html.escape(line[3:])}</li>')
            elif line.strip() == '':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
            else:
                if in_list: html_lines.append('</ul>'); in_list = False
                if 'Kết luận' in line or 'Tóm lại' in line or 'Conclusion' in line or 'Summary' in line:
                    html_lines.append(f'<div class="highlight">{line}</div>')
                else:
                    html_lines.append(f'<p>{line}</p>')
        if in_list:
            html_lines.append('</ul>')
        body_html = '\n'.join(html_lines)

    description = html_to_plain_text(content)[:160]

    if lang == "vi":
        canonical = f"https://webback.qzz.io/{slug}.html"
        article_url = f"https://webback.qzz.io/{slug}.html"
    else:
        canonical = f"https://webback.qzz.io/en/{slug}.html"
        article_url = f"https://webback.qzz.io/en/{slug}.html"

    html_template = f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {site_title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="AI, {tag}, ChatGPT, Claude, Gemini, công nghệ, trí tuệ nhân tạo, chatbot, automation">
    <meta name="author" content="Ninh Hoa Blog">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://picsum.photos/1200/630?random={slug}">
    <meta property="og:locale" content="{og_locale}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{article_url}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --gray-900: #1e293b;
            --gray-700: #334155;
            --gray-500: #64748b;
            --gray-300: #cbd5e1;
            --gray-100: #f1f5f9;
            --white: #ffffff;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: var(--gray-100); color: var(--gray-900); line-height: 1.7; -webkit-font-smoothing: antialiased; }}
        a {{ color: var(--primary); text-decoration: none; }}
        a:hover {{ color: var(--primary-dark); }}

        .article-header {{
            background: var(--white);
            border-bottom: 1px solid var(--gray-300);
            padding: 0 24px;
            height: 72px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-left {{ display: flex; align-items: center; gap: 12px; }}
        .logo {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--gray-900);
        }}
        .logo-icon {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: linear-gradient(135deg, #2563eb, #818cf8);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 12px;
        }}
        .header-nav {{ display: flex; align-items: center; gap: 24px; }}
        .header-nav a {{
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--gray-500);
            transition: color 0.2s;
        }}
        .header-nav a:hover, .header-nav a.active {{ color: var(--primary); }}
        .lang-switch {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: var(--gray-100);
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--gray-700);
            transition: background 0.2s;
        }}
        .lang-switch:hover {{ background: var(--gray-300); }}

        .article-hero {{
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 60px 24px 40px;
            text-align: center;
        }}
        .article-hero-inner {{ max-width: 750px; margin: 0 auto; }}
        .article-tag {{
            display: inline-block;
            padding: 4px 12px;
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .article-hero h1 {{
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 20px;
            letter-spacing: -0.02em;
        }}
        .article-meta {{
            display: flex;
            justify-content: center;
            gap: 24px;
            color: rgba(255,255,255,0.7);
            font-size: 0.9rem;
        }}
        .article-meta span {{ display: flex; align-items: center; gap: 6px; }}

        .article-container {{
            max-width: 750px;
            margin: -30px auto 60px;
            padding: 0 24px;
            position: relative;
        }}
        .article {{
            background: var(--white);
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02), 0 10px 30px rgba(0,0,0,0.04);
            border: 1px solid var(--gray-300);
        }}
        .article-featured-image {{
            margin-bottom: 32px;
            border-radius: 12px;
            overflow: hidden;
        }}
        .article-featured-image img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .article p {{
            margin-bottom: 20px;
            color: var(--gray-700);
            font-size: 1.05rem;
            line-height: 1.8;
        }}
        .article h2 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gray-900);
            margin: 40px 0 16px;
            padding-top: 20px;
            border-top: 1px solid var(--gray-100);
        }}
        .article h2:first-child {{ margin-top: 0; padding-top: 0; border-top: none; }}
        .article h3 {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--gray-900);
            margin: 30px 0 12px;
        }}
        .article ul, .article ol {{
            margin: 0 0 20px 24px;
            color: var(--gray-700);
        }}
        .article li {{
            margin-bottom: 10px;
            line-height: 1.7;
        }}
        .article strong {{ color: var(--gray-900); font-weight: 600; }}
        .article .highlight {{
            background: linear-gradient(135deg, #eef2ff, #e0e7ff);
            border-left: 4px solid var(--primary);
            padding: 20px 24px;
            border-radius: 0 12px 12px 0;
            margin: 30px 0;
            color: var(--gray-900);
            font-weight: 500;
        }}
        .article .highlight strong {{ display: block; margin-bottom: 8px; color: var(--primary); }}

        .share-section {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid var(--gray-100);
        }}
        .share-section p {{
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 16px;
            font-size: 1rem;
        }}
        .share-buttons {{ display: flex; gap: 12px; flex-wrap: wrap; }}
        .share-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            color: white;
            transition: all 0.2s;
        }}
        .share-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .share-btn.zalo {{ background: #0068FF; }}
        .share-btn.facebook {{ background: #1877F2; }}
        .share-btn.twitter {{ background: #1DA1F2; }}

        .related-section {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid var(--gray-100);
        }}
        .related-section h3 {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 20px;
        }}
        .related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        .related-card {{
            display: block;
            background: var(--gray-100);
            border: 1px solid var(--gray-300);
            border-radius: 12px;
            padding: 16px;
            transition: all 0.2s;
        }}
        .related-card:hover {{
            background: var(--gray-100);
            border-color: var(--primary);
            transform: translateY(-2px);
        }}
        .related-card h4 {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 6px;
            line-height: 1.4;
        }}
        .related-tag {{
            display: inline-block;
            background: #e0e7ff;
            color: #4338ca;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .article-footer {{
            text-align: center;
            padding: 40px 24px;
            color: var(--gray-500);
            font-size: 0.85rem;
            border-top: 1px solid var(--gray-300);
            margin-top: 60px;
            background: var(--white);
        }}
        .article-footer a {{
            color: var(--primary);
            font-weight: 500;
        }}

        @media (max-width: 600px) {{
            .article-header {{ height: auto; padding: 12px 16px; flex-direction: column; gap: 12px; }}
            .header-nav {{ display: none; }}
            .article-hero h1 {{ font-size: 1.6rem; }}
            .article-meta {{ flex-wrap: wrap; gap: 12px; }}
            .article {{ padding: 24px; }}
            .article h1 {{ font-size: 1.6rem; }}
            .share-buttons {{ flex-direction: column; }}
            .article-featured-image {{ margin-bottom: 24px; }}
        }}
    </style>
</head>
<body>
    <header class="article-header">
        <div class="header-left">
            <a href="{home_link}" class="logo">
                <div class="logo-icon">AI</div>
                <span>Ninh<span style="color: var(--primary);">Ho</span>a Blog</span>
            </a>
            <nav class="header-nav">
                <a href="{home_link}">Trang chu</a>
                <a href="{home_link}about.html">Gioi thieu</a>
            </nav>
        </div>
        <a class="lang-switch" href="{'/en/' if lang == 'vi' else '/'}{slug}.html">
            <i class="fas fa-globe"></i> {'English' if lang == 'vi' else 'Tiếng Việt'}
        </a>
    </header>

    <section class="article-hero">
        <div class="article-hero-inner">
            <span class="article-tag">{tag}</span>
            <h1>{title}</h1>
            <div class="article-meta">
                <span><i class="far fa-calendar"></i> {date_str}</span>
                <span><i class="fas fa-tag"></i> {tag}</span>
                <span><i class="far fa-clock"></i> {read_time}</span>
            </div>
        </div>
    </section>

    <div class="article-container">
        <article class="article">
            <div class="article-featured-image">
                <img src="https://picsum.photos/1200/630?random={slug}" alt="{title}" loading="lazy">
            </div>
            {body_html}

            <div class="share-section">
                <p>{share_text}</p>
                <div class="share-buttons">
                    <a href="https://zalo.me/share?url={article_url}" target="_blank" rel="noopener" class="share-btn zalo">
                        <i class="fab fa-zalo"></i> {zalo_text}
                    </a>
                    <a href="https://www.facebook.com/sharer/sharer.php?u={article_url}" target="_blank" rel="noopener" class="share-btn facebook">
                        <i class="fab fa-facebook-f"></i> {facebook_text}
                    </a>
                    <a href="https://twitter.com/intent/tweet?url={article_url}&text={title}" target="_blank" rel="noopener" class="share-btn twitter">
                        <i class="fab fa-twitter"></i> {twitter_text}
                    </a>
                </div>
            </div>
        </article>
    </div>

    <footer class="article-footer">
        <p>&copy; 2025 Ninh Hoa Blog. Tu dong van hanh boi AI.</p>
        <p><a href="{home_link}">← Ve trang chu</a></p>
    </footer>
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
        subprocess.run(["git", "config", "user.email", "agent@ninhhoa.blog"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "config", "user.name", "AI Agent"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    # Không cần clone/pull — GitHub Actions đã checkout sẵn
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