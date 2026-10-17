"""
DSA Agent — LangGraph pipeline that produces Theory, Pseudocode and Code
for any given Data Structures & Algorithms topic.

Ported from PyChamp.ipynb into a reusable module.
"""

import os
from typing import TypedDict
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

# ── Load environment variables ──────────────────────────────────────────────
# Check for .env in pychamp directory or workspace root
for _env_candidate in [
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
]:
    if _env_candidate.exists():
        load_dotenv(_env_candidate, override=True)
        break
os.environ.setdefault("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))


# ── State schema ────────────────────────────────────────────────────────────
class State(TypedDict, total=False):
    topic: str
    theory: str
    pseudocode: str
    code: str
    api_key: str


def _get_api_key(state: State) -> str:
    """Return user-provided API key from state or fallback to default from environment."""
    key = (state.get("api_key") or "").strip()
    if not key:
        key = os.getenv("GROQ_API_KEY", "").strip()
    return key


# ── Agent node functions ────────────────────────────────────────────────────
def produce_theory(state: State):
    prompt = ChatPromptTemplate.from_template(
        """ 
        You are an experienced professor in Data Structures & Algorithms.\n
        You are also an experienced Python developer.\n
        Use your Python & DSA skills to teach a young beginner the given topic:\n
        - Topic: {topic}\n
        Your task is to provide him a detailed and well-explained theory on the given topic.\n
        Include theoretical explanation, algorithm, complexities (if required).\n
        Don't include code in this! Keep it purely theoretical.\n
        Generate your response in a structured Markdown format.
        """
    )
    api_key = _get_api_key(state)
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, groq_api_key=api_key or None)
    chain = prompt | llm | StrOutputParser()
    theory = chain.invoke({"topic": state["topic"]})
    return {"theory": theory}


def produce_pseudocode(state: State):
    prompt = ChatPromptTemplate.from_template(
        """ 
        You are an experienced professor in Data Structures & Algorithms.\n
        You are also an experienced Python developer.\n
        Use your Python & DSA skills to teach a young beginner the given topic:\n
        - Topic: {topic}\n
        Your task is to only provide him the pseudocode of the given topic.\n
        Generate your response in a structured Markdown format and only include Pseudocode.
        """
    )
    api_key = _get_api_key(state)
    llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.2, groq_api_key=api_key or None)
    chain = prompt | llm | StrOutputParser()
    pseudocode = chain.invoke({"topic": state["topic"]})
    return {"pseudocode": pseudocode}


def produce_code(state: State):
    prompt = ChatPromptTemplate.from_template(
        """ 
        You are an experienced professor in Data Structures & Algorithms.\n
        You are also an experienced Python developer.\n
        Use your Python & DSA skills to teach a young beginner the given topic:\n
        - Topic: {topic}\n
        Your task is to provide him a clean and efficient Python code.\n
        After the code provide its step by step explanation with time & space complexities.\n
        Generate your response in a structured Markdown format.
        """
    )
    api_key = _get_api_key(state)
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2, groq_api_key=api_key or None)
    chain = prompt | llm | StrOutputParser()
    code = chain.invoke({"topic": state["topic"]})
    return {"code": code}


# ── Build the graph (three parallel agents) ─────────────────────────────────
def _build_graph():
    builder = StateGraph(State)
    builder.add_node("Theory", produce_theory)
    builder.add_node("Pseudocode", produce_pseudocode)
    builder.add_node("Code", produce_code)
    builder.add_edge(START, "Theory")
    builder.add_edge(START, "Pseudocode")
    builder.add_edge(START, "Code")
    builder.add_edge("Theory", END)
    builder.add_edge("Pseudocode", END)
    builder.add_edge("Code", END)
    return builder.compile()


# Compiled graph — ready to invoke
graph = _build_graph()


def invoke_dsa_agent(topic: str, api_key: str | None = None, user=None) -> dict:
    """
    Run the DSA agent pipeline for the given topic.

    Parameters:
    - topic: DSA topic to generate content for.
    - api_key: Optional custom Groq API key (e.g. from user profile).
    - user: Optional Django User or UserProfile instance to extract the key from.

    If no custom API key is present or provided, the default GROQ_API_KEY
    from the .env file / environment is used.

    Returns a dict with keys: topic, theory, pseudocode, code.
    """
    effective_key = (api_key or "").strip()
    if not effective_key and user is not None:
        profile = getattr(user, "profile", user)
        if hasattr(profile, "get_groq_api_key"):
            effective_key = profile.get_groq_api_key()
        elif hasattr(profile, "groq_api_key"):
            effective_key = (profile.groq_api_key or "").strip()

    # For standalone scripts/calls where no user is specified, allow .env fallback
    if not effective_key and user is None:
        effective_key = os.getenv("GROQ_API_KEY", "").strip()

    if not effective_key:
        raise ValueError("A valid Groq API key is required to invoke the DSA agent.")

    payload = {"topic": topic, "api_key": effective_key}
    result = graph.invoke(payload)
    return result

