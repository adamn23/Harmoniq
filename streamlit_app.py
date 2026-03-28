from __future__ import annotations
import os
import pickle
import pandas as pd
import streamlit as st
import graphviz

from SongTree import SongTree
from SongGraph import SongGraph
from data_preprocessing import load_graph

GRAPH_CACHE = "song_graph_cache.pkl"
TREE_CACHE = "song_tree_cache.parquet"
DATASET_NAME = "spotify_dataset"

st.set_page_config(
    page_title="Harmoniq Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at top left, rgba(77, 171, 247, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(168, 85, 247, 0.16), transparent 32%),
        linear-gradient(180deg, #07111f 0%, #0b1220 45%, #0f172a 100%);
    color: #e5eefb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

.hero {
    padding: 1.6rem 1.8rem;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(17,24,39,0.80));
    box-shadow: 0 24px 80px rgba(0,0,0,0.28);
    backdrop-filter: blur(14px);
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2rem, 4vw, 3.8rem);
    margin: 0;
    color: #f8fbff;
}

.hero p {
    color: #bfd0ea;
    font-size: 1.02rem;
    margin-top: 0.5rem;
}

.glass {
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 1.25rem;
    box-shadow: 0 18px 50px rgba(0,0,0,0.22);
}

.metric-card {
    border-radius: 18px;
    padding: 1rem 1.1rem;
    background: linear-gradient(180deg, rgba(30,41,59,0.78), rgba(15,23,42,0.88));
    border: 1px solid rgba(148,163,184,0.16);
}

.metric-label {
    font-size: 0.82rem;
    color: #9fb3d1;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f8fbff;
}

.question-box {
    border-radius: 22px;
    padding: 1.2rem 1.25rem;
    background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(99,102,241,0.15));
    border: 1px solid rgba(96,165,250,0.32);
}

.small-muted {
    color: #9fb3d1;
    font-size: 0.92rem;
}

.badge {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(56,189,248,0.14);
    border: 1px solid rgba(56,189,248,0.26);
    color: #d8f3ff;
    font-size: 0.82rem;
    margin-right: 0.45rem;
    margin-bottom: 0.35rem;
}

div.stButton > button {
    width: 100%;
    border-radius: 14px;
    height: 3rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.08);
    background: linear-gradient(180deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95));
    color: #f8fbff;
}

div.stButton > button:hover {
    border-color: rgba(125,211,252,0.65);
    color: white;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10,15,26,0.98), rgba(10,15,26,0.92));
    border-right: 1px solid rgba(255,255,255,0.06);
}
</style>
""",
    unsafe_allow_html=True,
)


def get_cached_graph(dataset_name: str) -> SongGraph:
    if os.path.exists(GRAPH_CACHE):
        with open(GRAPH_CACHE, "rb") as f:
            return pickle.load(f)

    graph, _ = load_graph(dataset_name, parquet_cache=TREE_CACHE)

    with open(GRAPH_CACHE, "wb") as f:
        pickle.dump(graph, f)

    return graph


def get_cached_dataframe(dataset_name: str) -> pd.DataFrame:
    if os.path.exists(TREE_CACHE):
        return pd.read_parquet(TREE_CACHE)

    _, df = load_graph(dataset_name, parquet_cache=TREE_CACHE)
    return df


@st.cache_resource(show_spinner=True)
def load_assets() -> tuple[pd.DataFrame, SongGraph]:
    df = get_cached_dataframe(DATASET_NAME)
    graph = get_cached_graph(DATASET_NAME)
    return df, graph


def init_game(force: bool = False) -> None:
    if force or "game_state" not in st.session_state:
        df, graph = load_assets()
        tree = SongTree(df, set())
        tree.update_split_scores()
        tree.update_question()

        st.session_state.df = df
        st.session_state.graph = graph
        st.session_state.game_state = tree
        st.session_state.history = []
        st.session_state.status = "playing"
        st.session_state.final_guess = None
        st.session_state.guess_queue = []


def build_tree_graph(history: list[dict], current_question: str, remaining_count: int) -> graphviz.Digraph:
    dot = graphviz.Digraph()
    dot.attr(rankdir="TB", bgcolor="transparent", pad="0.25", nodesep="0.35", ranksep="0.55")
    dot.attr("node", shape="box", style="rounded,filled", color="#334155", fontname="Helvetica", fontsize="11")
    dot.attr("edge", color="#64748b", fontname="Helvetica", fontsize="10")

    dot.node(
        "root",
        "Start\\nAll songs",
        fillcolor="#0f172a",
        fontcolor="#f8fafc",
        color="#38bdf8",
        penwidth="1.8",
    )
    parent = "root"

    if not history:
        dot.node(
            "current",
            f"Current\\n{current_question}\\n({remaining_count} songs left)",
            fillcolor="#1d4ed8",
            fontcolor="white",
            color="#93c5fd",
            penwidth="2.0",
        )
        dot.edge("root", "current", label="begin")
        return dot

    for i, step in enumerate(history, start=1):
        node_id = f"n{i}"
        outline = "#fbbf24"
        if step["answer"] == "yes":
            outline = "#34d399"
        elif step["answer"] == "no":
            outline = "#f87171"

        label = f"Q{i}\\n{step['question']}\\n{step['remaining']} songs left"
        dot.node(
            node_id,
            label,
            fillcolor="#0f172a",
            fontcolor="#e2e8f0",
            color=outline,
            penwidth="1.6",
        )
        dot.edge(parent, node_id, label=step["answer"].upper())
        parent = node_id

    dot.node(
        "current",
        f"Current\\n{current_question}\\n({remaining_count} songs left)",
        fillcolor="#1e293b",
        fontcolor="white",
        color="#c084fc",
        penwidth="2.0",
    )
    dot.edge(parent, "current", label="next")
    return dot


def evaluate_state() -> None:
    game_state = st.session_state.game_state
    graph = st.session_state.graph

    if len(game_state.df) == 0:
        st.session_state.status = "defeated"
        return

    if len(game_state.df) == 1:
        st.session_state.status = "solved"
        st.session_state.final_guess = game_state.df.iloc[0].to_dict()
        return

    if game_state.is_leaf():
        most_popular = game_state.df.loc[game_state.df["popularity"].idxmax()].to_dict()
        st.session_state.final_guess = most_popular

        wrong_song_id = int(most_popular["song_id"])
        similar_songs = graph.get_similar(wrong_song_id, limit=20)
        current_pool_ids = set(game_state.df["song_id"])

        remaining_df = game_state.df[game_state.df["song_id"] != wrong_song_id]
        remaining = remaining_df.to_dict("records")

        similar_ids_in_pool = [s.song_id for s in similar_songs if s.song_id in current_pool_ids]
        remaining.sort(key=lambda r: (0 if int(r["song_id"]) in similar_ids_in_pool else 1))

        st.session_state.guess_queue = remaining
        st.session_state.status = "guessing"
    else:
        st.session_state.status = "playing"


def advance_game(answer: str) -> None:
    game_state = st.session_state.game_state
    question = game_state.get_question()
    next_state = game_state.get_next_tree_state(answer)

    st.session_state.game_state = next_state
    st.session_state.history.append(
        {
            "question": question,
            "answer": answer,
            "remaining": len(next_state.df),
        }
    )

    evaluate_state()


def try_next_candidate() -> None:
    if st.session_state.guess_queue:
        st.session_state.final_guess = st.session_state.guess_queue.pop(0)
        st.session_state.status = "fallback"
    else:
        st.session_state.status = "defeated"


init_game()
df, _graph = load_assets()
game_state = st.session_state.game_state

with st.sidebar:
    st.markdown("## Harmoniq Studio")
    st.markdown("A Streamlit front end for your song tree and graph engine.")
    st.markdown(f"**Songs loaded:** {len(df):,}")
    st.markdown(f"**Questions answered:** {len(st.session_state.history)}")

    if st.button("Start new round"):
        init_game(force=True)
        st.rerun()

    st.markdown("---")
    st.markdown("### Path so far")

    if st.session_state.history:
        for i, step in enumerate(st.session_state.history, start=1):
            st.markdown(f"{i}. {step['answer'].upper()} — {step['question']}")
    else:
        st.caption("No answers yet.")

st.markdown(
    """
<div class="hero">
  <h1>Harmoniq Studio</h1>
  <p>Think of a song. The interface narrows the catalog with your answers and draws the live decision path as the tree forms.</p>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Songs in catalog</div><div class="metric-value">{len(df):,}</div></div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Candidates left</div><div class="metric-value">{len(game_state.df):,}</div></div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Questions answered</div><div class="metric-value">{len(st.session_state.history)}</div></div>',
        unsafe_allow_html=True,
    )

left, right = st.columns([1.05, 1.15], gap="large")

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Question flow")

    if st.session_state.status == "playing":
        st.markdown(
            f'<div class="question-box"><div class="small-muted">Current question</div><div style="font-size:1.35rem;font-weight:700;margin-top:0.35rem;color:#f8fbff;">{game_state.get_question()}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        a1, a2, a3 = st.columns(3)

        with a1:
            if st.button("Yes"):
                advance_game("yes")
                st.rerun()

        with a2:
            if st.button("No"):
                advance_game("no")
                st.rerun()

        with a3:
            if st.button("I don't know"):
                advance_game("i dont know")
                st.rerun()

        st.markdown(
            "<div class='small-muted' style='margin-top:0.8rem;'>The tree chooses the most balanced next split from your current candidate pool.</div>",
            unsafe_allow_html=True,
        )

    elif st.session_state.status == "solved":
        song = st.session_state.final_guess
        st.success(f"I think your song is **{song['song_name']}** by **{song['artists']}**.")

    elif st.session_state.status == "guessing":
        song = st.session_state.final_guess
        st.warning(f"I have narrowed it down. Is it **{song['song_name']}** by **{song['artists']}**?")

        g1, g2 = st.columns(2)
        with g1:
            if st.button("Yes, that's it"):
                st.session_state.status = "confirmed"
                st.rerun()
        with g2:
            if st.button("No, try another"):
                try_next_candidate()
                st.rerun()

    elif st.session_state.status == "fallback":
        song = st.session_state.final_guess
        st.info(f"Wait — is it **{song['song_name']}** by **{song['artists']}**?")

        f1, f2 = st.columns(2)
        with f1:
            if st.button("Yes, correct"):
                st.session_state.status = "confirmed"
                st.rerun()
        with f2:
            if st.button("No, keep going"):
                try_next_candidate()
                st.rerun()

    elif st.session_state.status == "confirmed":
        song = st.session_state.final_guess
        st.success(f"Locked in: **{song['song_name']}** by **{song['artists']}**.")
    else:
        st.error("Well played. I couldn't pin it down from the remaining pool.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Candidate snapshot")

    preview_cols = [c for c in ["song_name", "artists", "primary_genre", "popularity"] if c in game_state.df.columns]
    st.dataframe(game_state.df[preview_cols].head(8), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Live decision tree")

    current_q = game_state.get_question() if st.session_state.status == "playing" else "Decision reached"
    st.graphviz_chart(
        build_tree_graph(st.session_state.history, current_q, len(game_state.df)),
        use_container_width=True,
    )

    st.markdown(
        "<div class='small-muted'>Green means yes, red means no, amber means uncertainty, and purple marks the current frontier.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("How it works")
    st.markdown(
        "- The dataset becomes a pandas-backed decision tree for fast filtering.\n"
        "- Each question is selected to split the remaining songs as evenly as possible.\n"
        "- If multiple songs survive, the similarity graph suggests fallback guesses in a smarter order."
    )
    st.markdown("</div>", unsafe_allow_html=True)