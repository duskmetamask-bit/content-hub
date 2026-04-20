import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="Content Hub — Shut Up and Build", page_icon="")

st.markdown("""
<style>
body { background-color: #0d1117; color: #e6edf3; }
.stApp { background-color: #0d1117; }
h1 { color: #58a6ff; font-size: 2rem; }
h2 { color: #8b949e; font-size: 1.2rem; margin-top: 2rem; }
.content-card { 
    background: #161b22; 
    border: 1px solid #30363d; 
    border-radius: 8px; 
    padding: 1.5rem; 
    margin: 1rem 0;
    line-height: 1.7;
}
.category-label {
    color: #58a6ff;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📝 Content Hub")
st.markdown("### Shut Up and Build")
st.markdown("---")

# Load content from vault
vault_path = Path("~/.openclaw/vault/dawn-vault/shared/content").expanduser()

def parse_content_file(filepath):
    with open(filepath) as f:
        content = f.read()
    
    drafts = []
    current_draft = {}
    current_section = None
    
    for line in content.split('\n'):
        if line.startswith('### Draft'):
            if current_draft:
                drafts.append(current_draft)
            current_draft = {'title': line.replace('### Draft', '').strip(), 'body': []}
        elif line.strip() == '---':
            if current_draft and current_draft['body']:
                drafts.append(current_draft)
                current_draft = {}
        elif current_draft is not None:
            current_draft['body'].append(line)
    
    if current_draft and current_draft.get('body'):
        drafts.append(current_draft)
    
    return drafts

# Get latest content files
content_files = sorted(vault_path.glob("*.md"), reverse=True)[:7]  # Last 7 days

for f in content_files:
    date_str = f.stem.replace("2026-04-", "April ")
    st.markdown(f"#### 📅 {date_str}")
    
    try:
        drafts = parse_content_file(f)
        for draft in drafts:
            if draft.get('body'):
                body = '\n'.join(draft['body']).strip()
                if body:
                    st.markdown(f"<div class='content-card'>{body.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"Couldn't load: {e}")
    
    st.markdown("---")

st.markdown("*Content auto-synced from vault. Last updated: just now*")
