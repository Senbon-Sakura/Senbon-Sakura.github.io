#!/usr/bin/env python3
"""Convert translated markdown to styled Chinese HTML with sidebar TOC.

Includes:
- C/C++ auto-indentation (re-indents code blocks by brace nesting)
- Fix Mineru extraction artifacts (\\ in code)
- Dark Monokai-style code theme with line numbers
- Sidebar TOC with active section tracking
"""
import re
import markdown
from pathlib import Path
from html import escape


# ---------- C/C++ auto-indenter ----------

def _count_brace_delta(line):
    """Count net { } delta in a line, ignoring strings/comments/chars."""
    delta = 0
    in_string = False
    in_char = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        nxt = line[i + 1] if i + 1 < n else ''
        if in_line_comment:
            break
        if in_block_comment:
            if c == '*' and nxt == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if in_char:
            if c == '\\':
                i += 2
                continue
            if c == "'":
                in_char = False
            i += 1
            continue
        if c == '/' and nxt == '/':
            break
        if c == '/' and nxt == '*':
            in_block_comment = True
            i += 2
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == "'":
            in_char = True
            i += 1
            continue
        if c == '{':
            delta += 1
        elif c == '}':
            delta -= 1
        i += 1
    return delta


def _is_label(stripped):
    """Detect C/C++ labels like 'A:' 'Loop0:' (used in HLS for loop labels)."""
    # Plain label: identifier followed by colon, nothing else
    if re.match(r'^[A-Za-z_]\w*\s*:\s*$', stripped):
        return True
    # Label followed by inline comment
    if re.match(r'^[A-Za-z_]\w*\s*:\s*//', stripped):
        return True
    return False


def reindent_cpp(code):
    """Re-indent C/C++ code based on brace nesting."""
    # First, clean Mineru artifacts: stray backslashes like "{\\ " or "\\}"
    code = code.replace('{\\\\ ', '{ ')
    code = code.replace('\\\\}', '}')
    code = code.replace('\\\\ ', '')
    # Replace the "兴" typo from Mineru ( multiplication * misread)
    code = code.replace('兴', '*')

    lines = code.split('\n')
    out = []
    depth = 0
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            out.append('')
            continue

        starts_with_close = stripped[0] in '})]'
        is_label = _is_label(stripped)
        is_preprocessor = stripped.startswith('#')

        # Determine display depth for this line
        current_depth = depth
        if starts_with_close:
            current_depth = max(0, depth - 1)

        if is_preprocessor:
            indent_str = ''
        elif is_label:
            # Labels sit at the outer level; following code stays at same depth
            indent_str = '    ' * current_depth
        else:
            indent_str = '    ' * current_depth

        out.append(indent_str + stripped)

        # Update depth for next line based on net brace change
        if is_label:
            # Label doesn't change depth on its own
            delta = 0
        else:
            delta = _count_brace_delta(stripped)
        depth = max(0, depth + delta)

    return '\n'.join(out)


def preprocess_code_blocks(md_text):
    """Find fenced code blocks and re-indent C/C++ ones."""
    # Pattern: ```lang\n...code...\n```
    pattern = re.compile(r'```(c|cpp|c\+\+|h|hpp|verilog|vhdl|javascript|lisp|python|solidity|matlab|hcl|perl)?\n(.*?)\n```', re.DOTALL)

    def repl(m):
        lang = m.group(1) or ''
        code = m.group(2)
        # Re-indent C-like languages
        if lang in ('c', 'cpp', 'c++', 'h', 'hpp', '') or lang is None:
            code = reindent_cpp(code)
        return f'```{lang}\n{code}\n```'

    return pattern.sub(repl, md_text)


# ---------- TOC ----------

def slugify(text):
    s = re.sub(r'`+', '', text)
    s = re.sub(r'[*_~\[\](){}]', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'[^\w一-鿿\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip().lower())
    return s or 'section'


def extract_headings(md_text):
    headings = []
    in_code = False
    for line in md_text.splitlines():
        if re.match(r'^```', line):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.+?)\s*$', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            headings.append((level, text))
    return headings


def build_toc_html(headings, max_level=3):
    seen = {}
    items = []
    for level, text in headings:
        if level > max_level:
            continue
        slug = slugify(text)
        if slug in seen:
            seen[slug] += 1
            slug = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 0
        disp = re.sub(r'[*_`~]', '', text)
        items.append((level, slug, disp))

    html = ['<nav class="toc-nav"><ul>']
    prev_level = 0
    for level, slug, disp in items:
        if prev_level == 0:
            html.append(f'<li class="lvl-{level}"><a href="#{slug}">{escape(disp)}</a>')
            prev_level = level
        elif level > prev_level:
            html.append('<ul>' * (level - prev_level))
            html.append(f'<li class="lvl-{level}"><a href="#{slug}">{escape(disp)}</a>')
            prev_level = level
        elif level < prev_level:
            html.append('</li></ul>' * (prev_level - level))
            html.append('</li>')
            html.append(f'<li class="lvl-{level}"><a href="#{slug}">{escape(disp)}</a>')
            prev_level = level
        else:
            html.append('</li>')
            html.append(f'<li class="lvl-{level}"><a href="#{slug}">{escape(disp)}</a>')
    if prev_level > 0:
        html.append('</li>')
    html.append('</ul></nav>')
    return '\n'.join(html)


# ---------- HTML build ----------

def build_html(md_path, html_path, title):
    md_text = Path(md_path).read_text(encoding='utf-8')
    # Re-indent code blocks (fixes Mineru's lost indentation)
    md_text = preprocess_code_blocks(md_text)
    headings = extract_headings(md_text)

    extensions = [
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'sane_lists',
        'md_in_html',
    ]
    extension_configs = {
        'codehilite': {
            'noclasses': True,
            'pygments_style': 'monokai',
            'guess_lang': False,
            'linenums': False,
        },
        'toc': {
            'permalink': '🔗',
            'slugify': lambda s, sep: slugify(s),
            'title': '目录',
        },
    }

    body = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs=extension_configs,
        output_format='html5',
    )

    # Post-process: wrap each codehilite block in a .code-block container
    def _wrap_codehilite(m):
        attrs = m.group(1)
        inner = m.group(2)
        return f'<div class="code-block"><div class="codehilite"{attrs}>{inner}</div></div>'

    body = re.sub(
        r'<div class="codehilite"([^>]*)>(.*?)</div>',
        _wrap_codehilite,
        body,
        flags=re.DOTALL,
    )

    toc_sidebar = build_toc_html(headings, max_level=3)

    css = """
:root {
  --bg: #fafafa;
  --fg: #1a1a1a;
  --accent: #c8102e;
  --accent-dark: #8b0000;
  --code-bg: #f0f0f0;
  --border: #d0d0d0;
  --link: #0066cc;
  --sidebar-bg: #ffffff;
  --sidebar-w: 320px;
  --code-bg-dark: #1e1e1e;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 80px; }
body {
  font-family: "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", "Source Han Sans SC", -apple-system, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.8;
  margin: 0;
  padding: 0;
  font-size: 16px;
}

/* Top banner */
.header-banner {
  background: linear-gradient(135deg, #c8102e 0%, #8b0000 100%);
  color: white;
  padding: 1.6rem 2rem;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-banner h1 { color: white; border: none; margin: 0; font-size: 1.5em; }
.header-banner p { margin: 0.3em 0 0 0; opacity: 0.9; font-size: 0.9em; }
.menu-toggle {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.4);
  color: white;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1em;
  line-height: 1;
}
.menu-toggle:hover { background: rgba(255,255,255,0.35); }

/* Layout */
.layout {
  display: flex;
  align-items: flex-start;
  max-width: 1500px;
  margin: 0 auto;
}

/* Sidebar TOC */
.sidebar {
  width: var(--sidebar-w);
  position: sticky;
  top: 80px;
  height: calc(100vh - 80px);
  overflow-y: auto;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  padding: 1rem 0.5rem 1rem 1rem;
  flex-shrink: 0;
  box-shadow: 2px 0 8px rgba(0,0,0,0.03);
}
.sidebar h2.toc-title {
  font-size: 1.05em;
  color: var(--accent);
  margin: 0 0 0.6em 0;
  padding: 0 0.4em 0.5em;
  border-bottom: 2px solid var(--accent);
  text-align: center;
}
.toc-nav { font-size: 0.85em; }
.toc-nav ul { list-style: none; padding-left: 0; margin: 0; }
.toc-nav li { margin: 0; padding: 0; }
.toc-nav a {
  display: block;
  padding: 0.25em 0.5em;
  color: #333;
  border-left: 2px solid transparent;
  transition: all 0.15s;
  text-decoration: none;
  line-height: 1.4;
}
.toc-nav a:hover {
  background: #fff5f5;
  border-left-color: var(--accent);
  color: var(--accent);
}
.toc-nav li.lvl-1 > a {
  font-weight: 600;
  color: var(--accent-dark);
  margin-top: 0.4em;
}
.toc-nav li.lvl-2 > a { padding-left: 1.2em; font-size: 0.95em; }
.toc-nav li.lvl-3 > a { padding-left: 2.0em; font-size: 0.9em; color: #555; }
.toc-nav a.active {
  background: #fff0f0;
  border-left-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}

/* Main content */
.container {
  flex: 1;
  min-width: 0;
  padding: 2rem 3rem;
  background: white;
  min-height: calc(100vh - 80px);
  box-shadow: 0 0 20px rgba(0,0,0,0.05);
  max-width: 1180px;
}
h1, h2, h3, h4, h5, h6 {
  color: var(--accent);
  font-weight: 600;
  margin-top: 1.8em;
  margin-bottom: 0.8em;
  line-height: 1.3;
  scroll-margin-top: 90px;
}
h1 { font-size: 2em; border-bottom: 3px solid var(--accent); padding-bottom: 0.3em; }
h2 { font-size: 1.6em; border-bottom: 1px solid var(--border); padding-bottom: 0.2em; }
h3 { font-size: 1.3em; }
h4 { font-size: 1.1em; }
p { margin: 0.8em 0; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; border: 1px solid var(--border); }

/* Inline code */
code {
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Source Code Pro", Consolas, monospace;
  font-size: 0.9em;
  color: #c8102e;
}

/* ---------- Code block styling ---------- */
.code-block {
  position: relative;
  margin: 1.4em 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  border: 1px solid #2a2a2a;
}
.code-block::before {
  content: "CODE";
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.4);
  font-size: 0.65em;
  font-family: "JetBrains Mono", monospace;
  padding: 0.3em 0.8em;
  border-radius: 0 8px 0 4px;
  letter-spacing: 1px;
  z-index: 2;
  pointer-events: none;
}
.codehilite {
  margin: 0 !important;
  background: #1e1e1e !important;
  overflow-x: auto;
}
.codehilite pre {
  background: #1e1e1e !important;
  color: #f8f8f2;
  padding: 1.2em 1.5em !important;
  margin: 0 !important;
  border-radius: 0 !important;
  line-height: 1.55 !important;
  font-size: 0.85em !important;
  font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Source Code Pro", Consolas, monospace !important;
  tab-size: 4;
  -moz-tab-size: 4;
}

/* Line numbers table from codehilite linenums=table */
.codehilite table {
  width: 100%;
  margin: 0 !important;
  border: none !important;
  background: transparent !important;
  font-size: inherit !important;
}
.codehilite td {
  border: none !important;
  padding: 0 !important;
  background: transparent !important;
}
.codehilite .linenos {
  background: #2a2a2a !important;
  color: #6e7681 !important;
  padding: 0 0.8em 0 0.5em !important;
  text-align: right !important;
  border-right: 1px solid #404040 !important;
  width: 1%;
  white-space: nowrap;
  user-select: none;
}
.codehilite .linenos .normal {
  color: #6e7681 !important;
  background: transparent !important;
}
.codehilite .code {
  padding: 0 0 0 1em !important;
  background: transparent !important;
}
.codehilite .code pre {
  padding: 0 !important;
  background: transparent !important;
  white-space: pre;
}

/* Monokai inline token colors (force override of inline styles where needed) */
.codehilite code { color: #f8f8f2; background: transparent; padding: 0; font-size: inherit; }
.codehilite .c, .codehilite .c1, .codehilite .cm { color: #75715e; font-style: italic; }
.codehilite .k, .codehilite .kc, .codehilite .kd, .codehilite .kp, .codehilite .kr { color: #66d9ef; font-style: italic; }
.codehilite .kt { color: #66d9ef; font-style: italic; }
.codehilite .s, .codehilite .s1, .codehilite .s2 { color: #e6db74; }
.codehilite .se, .codehilite .sr { color: #e6db74; }
.codehilite .n, .codehilite .nx { color: #f8f8f2; }
.codehilite .nf { color: #a6e22e; }
.codehilite .nc { color: #a6e22e; font-weight: bold; }
.codehilite .nn { color: #a6e22e; }
.codehilite .nb { color: #66d9ef; }
.codehilite .bp { color: #66d9ef; }
.codehilite .m, .codehilite .mi, .codehilite .mf, .codehilite .mh { color: #ae81ff; }
.codehilite .o { color: #f92672; }
.codehilite .p { color: #f8f8f2; }
.codehilite .cp { color: #75715e; }
.codehilite .cp .c1 { color: #75715e; }
.codehilite .err { color: #f8f8f2; background: transparent; }
.codehilite .g { color: #f8f8f2; }
.codehilite .gd { color: #f92672; }
.codehilite .gi { color: #a6e22e; }

/* Plain code blocks (no language) */
pre:not(.codehilite pre) {
  background: #1e1e1e;
  color: #f8f8f2;
  padding: 1.2em 1.5em;
  border-radius: 8px;
  overflow-x: auto;
  line-height: 1.55;
  font-size: 0.85em;
  font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Source Code Pro", Consolas, monospace;
  margin: 1.4em 0;
  border: 1px solid #2a2a2a;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  font-size: 0.95em;
}
th, td {
  border: 1px solid var(--border);
  padding: 0.6em 0.9em;
  text-align: left;
}
th { background: #f5f5f5; font-weight: 600; }
tr:nth-child(even) { background: #fafafa; }
blockquote {
  border-left: 4px solid var(--accent);
  margin: 1em 0;
  padding: 0.5em 1.2em;
  background: #fff8f8;
  color: #444;
}
hr {
  border: none;
  border-top: 2px dashed var(--border);
  margin: 2.5em 0;
}
ul, ol { padding-left: 2em; }
li { margin: 0.3em 0; }

/* Back to top button */
.back-to-top {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent);
  color: white;
  border: none;
  font-size: 1.4em;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(200,16,46,0.4);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
  z-index: 99;
}
.back-to-top.visible { opacity: 1; visibility: visible; }
.back-to-top:hover { background: var(--accent-dark); transform: translateY(-3px); }

/* Sidebar overlay for mobile */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 90;
}
.sidebar-overlay.show { display: block; }

/* Mobile responsive */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 95;
    transform: translateX(-100%);
    transition: transform 0.3s;
    width: 280px;
    padding-top: 2rem;
  }
  .sidebar.open { transform: translateX(0); }
  .container { padding: 1.5rem; max-width: 100%; }
  .header-banner { padding: 1rem; }
  .header-banner h1 { font-size: 1.2em; }
}
@media print {
  .sidebar, .back-to-top, .menu-toggle { display: none; }
  .container { max-width: none; box-shadow: none; padding: 0; }
  body { font-size: 11pt; }
  .header-banner { position: static; }
  .code-block { box-shadow: none; page-break-inside: avoid; }
}
"""

    js = """
// Toggle sidebar on mobile
document.querySelector('.menu-toggle')?.addEventListener('click', () => {
  document.querySelector('.sidebar').classList.toggle('open');
  document.querySelector('.sidebar-overlay').classList.toggle('show');
});
document.querySelector('.sidebar-overlay')?.addEventListener('click', () => {
  document.querySelector('.sidebar').classList.remove('open');
  document.querySelector('.sidebar-overlay').classList.remove('show');
});

// Back to top button
const btn = document.querySelector('.back-to-top');
window.addEventListener('scroll', () => {
  if (window.scrollY > 400) btn.classList.add('visible');
  else btn.classList.remove('visible');
});
btn?.addEventListener('click', () => window.scrollTo({top: 0, behavior: 'smooth'}));

// Active TOC link tracking via IntersectionObserver
const headings = document.querySelectorAll('h1[id], h2[id], h3[id]');
const tocLinks = document.querySelectorAll('.toc-nav a');
const linkMap = new Map();
tocLinks.forEach(a => {
  const href = a.getAttribute('href');
  if (href && href.startsWith('#')) linkMap.set(href.slice(1), a);
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      tocLinks.forEach(l => l.classList.remove('active'));
      const active = linkMap.get(id);
      if (active) {
        active.classList.add('active');
        const sidebar = document.querySelector('.sidebar');
        const linkTop = active.getBoundingClientRect().top;
        const sidebarTop = sidebar.getBoundingClientRect().top;
        const sidebarH = sidebar.clientHeight;
        if (linkTop < sidebarTop + 50 || linkTop > sidebarTop + sidebarH - 50) {
          active.scrollIntoView({block: 'nearest', behavior: 'smooth'});
        }
      }
    }
  });
}, { rootMargin: '-80px 0px -70% 0px', threshold: 0 });
headings.forEach(h => observer.observe(h));

// Copy code on click (bonus)
document.querySelectorAll('.code-block').forEach(block => {
  block.addEventListener('dblclick', () => {
    const code = block.querySelector('code');
    if (code && navigator.clipboard) {
      navigator.clipboard.writeText(code.textContent).then(() => {
        const label = block.querySelector('::before');
        block.style.outline = '2px solid #66d9ef';
        setTimeout(() => block.style.outline = '', 300);
      });
    }
  });
});
"""

    html = f"""---
layout: false
---
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div class="header-banner">
  <button class="menu-toggle" aria-label="目录">☰ 目录</button>
  <h1>Vitis 高层次综合用户指南</h1>
  <p>UG1399 (v2026.1) · 中文翻译版 · 2026 年 6 月 23 日</p>
</div>
<div class="layout">
  <aside class="sidebar">
    <h2 class="toc-title">📑 文档目录</h2>
    {toc_sidebar}
  </aside>
  <div class="sidebar-overlay"></div>
  <main class="container">
{body}
  </main>
</div>
<button class="back-to-top" aria-label="返回顶部">↑</button>
<script>
{js}
</script>
</body>
</html>
"""
    Path(html_path).write_text(html, encoding='utf-8')
    print(f"Built {html_path} ({len(html):,} bytes)")
    print(f"TOC entries: {len(headings)} headings")


if __name__ == '__main__':
    base = '/home/wangzongwu/Documents/BookTranslation/Vitis高层次综合用户指南_en/output'
    build_html(f'{base}/vitis_hls_zh.md', f'{base}/vitis_hls_zh.html', 'Vitis 高层次综合用户指南')
