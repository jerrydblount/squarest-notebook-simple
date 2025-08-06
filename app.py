"""
Squarest Notebook Simple - A reliable, deployable notebook application
Built with Streamlit and SQLite for maximum compatibility
"""

import os
import streamlit as st
from pathlib import Path
from datetime import datetime
import tempfile

from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Import our modules
import database as db
from ai_chat import chat_with_ai, get_available_models
from document_processor import process_document

# Page configuration
st.set_page_config(
    page_title="Squarest Notebook",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'sources' not in st.session_state:
    st.session_state.sources = []
if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = []
if 'selected_source' not in st.session_state:
    st.session_state.selected_source = None


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.title("📓 Squarest Notebook")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigate",
            ["📚 Sources", "💬 Chat", "📝 Notes", "🎙️ Podcasts", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        # Quick stats
        sources = db.get_sources()
        notes = db.get_notes()
        conversations = db.get_conversations()
        
        st.metric("Sources", len(sources))
        st.metric("Notes", len(notes))
        st.metric("Conversations", len(conversations))
    
    # Main content area
    if page == "📚 Sources":
        show_sources_page()
    elif page == "💬 Chat":
        show_chat_page()
    elif page == "📝 Notes":
        show_notes_page()
    elif page == "🎙️ Podcasts":
        show_podcasts_page()
    elif page == "⚙️ Settings":
        show_settings_page()


def show_sources_page():
    """Sources management page"""
    st.title("📚 Knowledge Sources")
    
    # Upload section
    st.subheader("Add New Source")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=['txt', 'pdf', 'md', 'docx', 'csv'],
            help="Upload a document to add to your knowledge base"
        )
        
        if uploaded_file:
            with st.spinner("Processing document..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name
                
                # Process the document
                try:
                    content = process_document(tmp_path, uploaded_file.type)
                    
                    # Create source in database
                    source_id = db.create_source(
                        title=uploaded_file.name,
                        content=content,
                        file_type=uploaded_file.type,
                        metadata={"size": uploaded_file.size}
                    )
                    
                    st.success(f"✅ Added: {uploaded_file.name}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                finally:
                    # Clean up temp file
                    Path(tmp_path).unlink(missing_ok=True)
    
    with col2:
        # URL input
        url = st.text_input("Or add from URL", placeholder="https://example.com/article")
        if st.button("Add URL", disabled=not url):
            with st.spinner("Fetching content..."):
                try:
                    # For now, just save the URL
                    source_id = db.create_source(
                        title=url,
                        url=url,
                        file_type="url"
                    )
                    st.success(f"✅ Added URL: {url}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding URL: {str(e)}")
    
    st.markdown("---")
    
    # Display existing sources
    st.subheader("Your Sources")
    
    sources = db.get_sources()
    
    if sources:
        for source in sources:
            with st.expander(f"📄 {source['title']}", expanded=False):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(f"Type: {source.get('file_type', 'Unknown')}")
                    st.text(f"Added: {source['created_at']}")
                    
                with col2:
                    if st.button("View", key=f"view_{source['id']}"):
                        st.session_state.selected_source = source['id']
                        
                with col3:
                    if st.button("Delete", key=f"del_{source['id']}", type="secondary"):
                        db.delete_source(source['id'])
                        st.rerun()
                
                # Show content preview if selected
                if st.session_state.selected_source == source['id'] and source.get('content'):
                    st.markdown("**Content Preview:**")
                    st.text_area(
                        "Content",
                        value=source['content'][:1000] + "..." if len(source.get('content', '')) > 1000 else source.get('content', ''),
                        height=200,
                        disabled=True
                    )
    else:
        st.info("No sources added yet. Upload a document or add a URL to get started!")


def show_chat_page():
    """AI Chat page"""
    st.title("💬 AI Chat")
    
    # Model selection
    models = get_available_models()
    selected_model = st.selectbox("Select AI Model", models, index=0)
    
    # Source context selection
    sources = db.get_sources()
    if sources:
        source_titles = ["No context"] + [s['title'] for s in sources]
        selected_source_idx = st.selectbox("Use source as context", range(len(source_titles)), 
                                          format_func=lambda x: source_titles[x])
        
        context = None
        if selected_source_idx > 0:
            source = sources[selected_source_idx - 1]
            context = source.get('content', '')
    else:
        context = None
    
    st.markdown("---")
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = chat_with_ai(
                        prompt,
                        model=selected_model,
                        context=context,
                        history=st.session_state.messages[:-1]  # Exclude current message
                    )
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Save conversation
                    if len(st.session_state.messages) > 1:
                        db.create_conversation(
                            messages=st.session_state.messages,
                            title=st.session_state.messages[0]["content"][:50],
                            model=selected_model
                        )
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


def show_notes_page():
    """Notes management page"""
    st.title("📝 Notes")
    
    # Create new note
    st.subheader("Create Note")
    
    note_title = st.text_input("Title (optional)")
    note_content = st.text_area("Content", height=150)
    
    # Link to source
    sources = db.get_sources()
    source_options = ["No source"] + [s['title'] for s in sources]
    selected_source_idx = st.selectbox("Link to source", range(len(source_options)),
                                       format_func=lambda x: source_options[x])
    
    if st.button("Save Note", disabled=not note_content):
        source_id = sources[selected_source_idx - 1]['id'] if selected_source_idx > 0 else None
        db.create_note(
            content=note_content,
            title=note_title if note_title else None,
            source_id=source_id
        )
        st.success("Note saved!")
        st.rerun()
    
    st.markdown("---")
    
    # Display notes
    st.subheader("Your Notes")
    
    notes = db.get_notes()
    
    if notes:
        for note in notes:
            with st.expander(f"📝 {note.get('title', 'Untitled Note')}", expanded=False):
                st.markdown(note['content'])
                st.caption(f"Created: {note['created_at']}")
                if note.get('source_id'):
                    source = db.get_source(note['source_id'])
                    if source:
                        st.caption(f"Source: {source['title']}")
    else:
        st.info("No notes yet. Create your first note above!")


def show_podcasts_page():
    """Podcasts page"""
    st.title("🎙️ Podcasts")
    
    st.info("Podcast generation coming soon! This feature will allow you to create AI-generated podcasts from your sources.")
    
    # Placeholder for podcast functionality
    podcasts = db.get_podcasts()
    
    if podcasts:
        for podcast in podcasts:
            with st.expander(f"🎙️ {podcast['title']}", expanded=False):
                st.markdown(podcast.get('transcript', 'No transcript available'))
                if podcast.get('audio_url'):
                    st.audio(podcast['audio_url'])
    else:
        st.info("No podcasts generated yet.")


def show_settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    
    st.subheader("API Keys")
    st.info("Configure your API keys in the .env file or environment variables")
    
    # Show configured providers
    st.subheader("Configured AI Providers")
    
    providers = {
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "Google AI": bool(os.getenv("GOOGLE_API_KEY")),
    }
    
    for provider, configured in providers.items():
        if configured:
            st.success(f"✅ {provider}")
        else:
            st.warning(f"⚠️ {provider} - Not configured")
    
    st.markdown("---")
    
    st.subheader("Database")
    st.info(f"Using SQLite database at: data/notebook.db")
    
    # Database stats
    sources = db.get_sources()
    notes = db.get_notes()
    conversations = db.get_conversations()
    podcasts = db.get_podcasts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Sources", len(sources))
        st.metric("Total Notes", len(notes))
    with col2:
        st.metric("Total Conversations", len(conversations))
        st.metric("Total Podcasts", len(podcasts))


if __name__ == "__main__":
    main()
