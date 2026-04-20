import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import re

st.set_page_config(page_title="Content Hub — Shut Up and Build", page_icon="")

st.markdown("""
<style>
body { background-color: #0d1117; color: #e6edf3; }
.stApp { background-color: #0d1117; }
h1 { color: #58a6ff; font-size: 2rem; }
h2 { color: #8b949e; font-size: 1.2rem; margin-top: 1.5rem; }
h3 { color: #e6edf3; font-size: 1rem; margin-top: 1rem; }
.content-card { 
    background: #161b22; 
    border: 1px solid #30363d; 
    border-radius: 8px; 
    padding: 1.5rem; 
    margin: 0.75rem 0;
    line-height: 1.8;
}
.success-box {
    background: #0d3320;
    border: 1px solid #2ea043;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    color: #2ea043;
    margin: 1rem 0;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

st.title("📝 Content Hub")
st.markdown("**Shut Up and Build**")
st.markdown("---")

# Vault path - use home directory expansion
VAULT_BASE = Path(os.path.expanduser("~/.openclaw/vault/dawn-vault/shared/content"))
APPROVED_DIR = VAULT_BASE / "approved"
MAYA_REF = VAULT_BASE / "maya-reference.md"

# Init session state
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'draft_data' not in st.session_state:
    st.session_state.draft_data = {}
if 'saved' not in st.session_state:
    st.session_state.saved = False

# Top controls
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✏️ Edit Mode" if not st.session_state.edit_mode else "🚫 Exit Edit"):
        st.session_state.edit_mode = not st.session_state.edit_mode
        st.session_state.saved = False
        st.rerun()

with col2:
    if st.session_state.edit_mode and st.button("💾 Save to Vault"):
        # Save all drafts
        APPROVED_DIR.mkdir(parents=True, exist_ok=True)
        
        for date_key, full_text in st.session_state.draft_data.items():
            if full_text.strip():
                # Figure out actual filename
                date_str = date_key.replace("April ", "2026-04-")
                original_file = VAULT_BASE / f"{date_str}.md"
                
                # Write to original file
                if original_file.exists():
                    with open(original_file, 'w') as f:
                        f.write(full_text)
                
                # Write to approved folder
                approved_file = APPROVED_DIR / f"{date_str}.md"
                with open(approved_file, 'w') as f:
                    f.write(full_text)
        
        # Append to Maya reference
        maya_entry = f"\n\n## Saved for Maya — {datetime.now().strftime('%B %d, %Y')}\n"
        for date_key, full_text in st.session_state.draft_data.items():
            if full_text.strip():
                maya_entry += f"\n{full_text}\n"
        
        with open(MAYA_REF, 'a') as f:
            f.write(maya_entry)
        
        st.session_state.saved = True
        st.rerun()

if st.session_state.saved:
    st.markdown('<div class="success-box">✅ Saved — Synced to Maya reference</div>', unsafe_allow_html=True)

st.markdown("---")

def parse_content_file(filepath):
    """Parse a content markdown file into drafts"""
    with open(filepath) as f:
        content = f.read()
    
    drafts = []
    current = {}
    
    for line in content.split('\n'):
        if line.startswith('### Draft'):
            if current and current.get('body'):
                drafts.append(current)
            current = {'title': line.replace('### Draft', '').strip(), 'body': [line]}
        elif line.strip() == '---':
            if current and current.get('body'):
                current['body'].append(line)
                drafts.append(current)
                current = {}
            else:
                current['body'].append(line)
        else:
            if current:
                current['body'].append(line)
    
    if current and current.get('body'):
        drafts.append(current)
    
    return drafts

def drafts_to_text(drafts, date_str):
    """Convert parsed drafts back to markdown text"""
    lines = [f"# Content — {date_str}\n", "## DRAFTS — Ready for Quality Check\n"]
    for i, d in enumerate(drafts, 1):
        lines.append(f"### Draft {i}: {d.get('title', '')}\n")
        lines.extend(d.get('body', []))
        lines.append('\n---\n')
    return '\n'.join(lines)

# Load and display content
try:
    content_files = sorted(VAULT_BASE.glob("2026-*.md"), reverse=True)[:7]
    
    for f in content_files:
        date_str = f.stem.replace("2026-04-", "April ")
        
        # Normalize date for state key
        date_key = date_str
        
        if date_key not in st.session_state.draft_data:
            st.session_state.draft_data[date_key] = f.read()
        
        st.markdown(f"### 📅 {date_str}")
        
        if st.session_state.edit_mode:
            edited = st.text_area(
                "",
                value=st.session_state.draft_data[date_key],
                height=350,
                label_visibility="collapsed",
                key=f"edit_{date_key}"
            )
            st.session_state.draft_data[date_key] = edited
        else:
            drafts = parse_content_file(f)
            for d in drafts:
                body = '\n'.join(d.get('body', [])).strip().replace('\n', '<br>')
                if body:
                    st.markdown(f"<div class='content-card'>{body}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
except Exception as e:
    st.error(f"Error loading content: {e}")

st.caption("*Content synced from vault. Edit mode saves to vault + Maya reference.*")