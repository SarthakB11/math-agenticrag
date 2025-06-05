import streamlit as st

CONFIG = {
    "llm": {
        "api_key": st.secrets["llm"]["api_key"]
    },
    "vector_db": {
        "url": st.secrets["vector_db"]["url"],
        "api_key": st.secrets["vector_db"]["api_key"],
        "port": st.secrets["vector_db"]["port"],
        "collection": st.secrets["vector_db"]["collection"]
    },
    "search": {
        "api_key": st.secrets["search"]["api_key"]
    },
    "database": {
        "connection_string": st.secrets["database"]["connection_string"]
    },
    "app": {
        "debug": st.secrets["app"]["debug"],
        "log_level": st.secrets["app"]["log_level"]
    }
}
