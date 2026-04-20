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
h2 { color: #8b949e; font-size: 1.2rem; margin-top: 2rem; }
h3 { color: #e6edf3; font-size: 1rem; margin-top: 1rem; }
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
.success-msg {
    background: #0d3320;
    border: 1px solid #2ea043;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    color: #2ea043;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.title("📝 Content Hub")
st.markdown("### Shut Up and Build")
st.markdown("---")

# Session state for edit mode and drafts
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'draft_states' not in st.session_state:
    st.session_state.draft_states = {}

# Toggle edit mode
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✏️ Edit Mode" if not st.session_state.edit_mode else "🚫 Exit Edit"):
        st.session_state.edit_mode = not st.session_state.edit_mode
        st.rerun()

with col2:
    if st.session_state.edit_mode:
        if st.button("💾 Save All"):
            vault_path = Path("~/.openclaw/vault/dawn-vault/shared/content").expanduser()
            approved_path = vault_path / "approved"
            approved_path.mkdir(exist_ok=True)
            maya_ref_path = Path("~/.openclaw/vault/dawn-vault/shared/content/maya-reference.md")
            
            for date_key, content in st.session_state.draft_states.items():
                if content.strip():
                    # Save to original file
                    date_normalized = date_key.replace("April ", "2026-04-")
                    original_file = vault_path / f"{date_normalized}.md"
                    if original_file.exists():
                        with open(original_file, 'w') as f:
                            f.write(content)
                    
                    # Save to approved folder
                    approved_file = approved_path / f"{date_normalized}.md"
                    with open(approved_file, 'w') as f:
                        f.write(content)
            
            # Append to Maya reference
            maya_header = f"\n## Saved for Maya — {datetime.now().strftime('%B %d, %Y')}\n"
            maya_content = maya_header + "\n".join(st.session_state.draft_states.values())
            with open(maya_ref_path, 'a') as f:
                f.write(maya_content)
            
            st.markdown('<div class="success-msg">✅ Saved — Content synced for Maya</div>', unsafe_allow_html=True)

st.markdown("---")

# Load content from vault
vault_path = Path("~/.openclaw/vault/dawn-vault/shared/content").expanduser()

def parse_content_file(filepath):
    with open(filepath) as f:
        content = f.read()
    
    drafts = []
    current_draft = {}
    
    for line in content.split('\n'):
        if line.startswith('### Draft'):
            if current_draft and current_draft.get('body'):
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

def drafts_to_text(drafts, date_str):
    text = f"## DRAFTS — Ready for Quality Check\n\n"
    for i, draft in enumerate(drafts, 1):
        text += f"### Draft {i}: {draft.get('title', '')}\n"
        text += '\n'.join(draft.get('body', [])) + '\n'
        text += '\n---\n\n'
    return text

# Get latest content files
content_files = sorted(vault_path.glob("*.md"), reverse=True)[:7]

for f in content_files:
    date_str = f.stem.replace("2026-04-", "April ")
    date_key = date_str
    
    st.markdown(f"#### 📅 {date_str}")
    
    try:
        drafts = parse_content_file(f)
        
        if st.session_state.edit_mode:
            # Edit mode — build full text for this date
            full_text = drafts_to_text(drafts, date_str)
            
            if date_key not in st.session_state.draft_states:
                st.session_state.draft_states[date_key] = full_text
            
            edited = st.text_area(
                f"Edit {date_str}",
                value=st.session_state.draft_states[date_key],
                height=400,
                label_visibility="collapsed",
                key=f"draft_{date_key}"
            )
            st.session_state.draft_states[date_key] = edited
        else:
            # Read mode
            for draft in drafts:
                if draft.get('body'):
                    body = '\n'.join(draft['body']).strip()
                    if body:
                        st.markdown(f"<div class='content-card'>{body.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"Couldn't load: {e}")
    
    st.markdown("---")

st.markdown("*Content auto-synced from vault*")
