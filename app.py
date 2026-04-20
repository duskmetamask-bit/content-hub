import streamlit as st
import os
from pathlib import Path
from datetime import datetime

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

# Use local content folder (synced from vault)
CONTENT_DIR = Path(__file__).parent / "content"
VAULT_CONTENT = Path(os.path.expanduser("~/.openclaw/vault/dawn-vault/shared/content"))

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
        from pathlib import Path
        
        VAULT_BASE = Path(os.path.expanduser("~/.openclaw/vault/dawn-vault/shared/content"))
        APPROVED_DIR = VAULT_BASE / "approved"
        MAYA_REF = VAULT_BASE / "maya-reference.md"
        
        APPROVED_DIR.mkdir(parents=True, exist_ok=True)
        
        for date_key, full_text in st.session_state.draft_data.items():
            if full_text.strip():
                date_str = date_key.replace("April ", "2026-04-")
                original_file = VAULT_BASE / f"{date_str}.md"
                
                if original_file.exists():
                    with open(original_file, 'w') as f:
                        f.write(full_text)
                
                approved_file = APPROVED_DIR / f"{date_str}.md"
                with open(approved_file, 'w') as f:
                    f.write(full_text)
        
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

def parse_content_file(content):
    """Parse content string into drafts"""
    drafts = []
    current = {}
    
    for line in content.split('\n'):
        if line.startswith('### Draft'):
            if current and current.get('body'):
                drafts.append(current)
            current = {'title': line.replace('### Draft', '').strip(), 'body': [line]}
        elif line.strip() == '---':
            if current and current.get('body'):
                drafts.append(current)
                current = {}
        else:
            if current or line.startswith('#'):
                if current is None:
                    current = {'body': []}
                current['body'].append(line)
    
    if current and current.get('body'):
        drafts.append(current)
    
    return drafts

# Load from local content folder (works on Vercel)
content_files = sorted(CONTENT_DIR.glob("2026-*.md"), reverse=True)[:7]

for f in content_files:
    date_str = f.stem.replace("2026-04-", "April ")
    date_key = date_str
    
    if date_key not in st.session_state.draft_data:
        st.session_state.draft_data[date_key] = f.read_text()
    
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
        content = st.session_state.draft_data[date_key]
        drafts = parse_content_file(content)
        for d in drafts:
            body = '\n'.join(d.get('body', [])).strip().replace('\n', '<br>')
            if body and not body.startswith('<br>'):
                st.markdown(f"<div class='content-card'>{body}</div>", unsafe_allow_html=True)
    
    st.markdown("---")

st.caption("*Content synced from vault. Edit mode saves to vault + Maya reference.*")