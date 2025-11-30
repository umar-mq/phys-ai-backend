from agents import function_tool
import arxiv
from app.vector_store import vector_store

@function_tool
async def search_coursebook(query: str) -> str:
    """
    Search the coursebook/knowledge base for relevant information to answer questions.
    Use this tool when you need factual information from the uploaded content.
    """
    return await vector_store.search(query)

@function_tool
def search_arxiv_papers(topic: str) -> str:
    """
    Search Arxiv for the latest research papers and developments regarding a specific topic.
    Returns summaries of the top 3 most recent relevant papers.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=3,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    results = []
    for r in client.results(search):
        results.append(f"Title: {r.title}\nDate: {r.published}\nSummary: {r.summary}\nLink: {r.entry_id}\n")
    
    if not results:
        return "No recent papers found."
    
    return "\n---\n".join(results)