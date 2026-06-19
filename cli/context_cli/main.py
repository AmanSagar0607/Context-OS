"""
Context OS — CLI Main

Entry point for the context command.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from . import __version__

console = Console()

API_URL = os.getenv("CONTEXT_API_URL", os.getenv("CONTEXT_OS_URL", "http://localhost:8000"))
API_KEY = os.getenv("CONTEXT_API_KEY", os.getenv("CONTEXT_OS_API_KEY"))


def _get_client():
    """Get HTTP client for API calls."""
    import httpx

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    return httpx.Client(
        base_url=API_URL,
        headers=headers,
        timeout=30.0,
    )


@click.group()
@click.version_option(version=__version__, prog_name="context-cli")
@click.option("--url", envvar="CONTEXT_API_URL", default="http://localhost:8000", help="API server URL")
@click.option("--key", envvar="CONTEXT_API_KEY", default=None, help="API key")
@click.pass_context
def cli(ctx: click.Context, url: str, key: Optional[str]):
    """Context OS — AI Agent Infrastructure CLI"""
    ctx.ensure_object(dict)
    ctx.obj["url"] = url
    ctx.obj["key"] = key


# --- Memory Commands ---

@cli.group()
def memory():
    """Memory operations"""
    pass


@memory.command("add")
@click.option("--content", "-c", required=True, help="Memory content")
@click.option("--type", "memory_type", default="episodic", help="Memory type (episodic/semantic/procedural)")
@click.option("--importance", default="medium", help="Importance (low/medium/high/critical)")
@click.option("--tags", help="Comma-separated tags")
@click.pass_context
def memory_add(ctx: click.Context, content: str, memory_type: str, importance: str, tags: Optional[str]):
    """Add a new memory"""
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    payload = {
        "content": content,
        "memory_type": memory_type,
        "importance": importance,
        "tags": tag_list,
    }

    with _get_client() as client:
        response = client.post("/api/v1/memory", json=payload)
        data = response.json()

        console.print(Panel(
            f"[green]✓[/green] Memory created: [bold]{data['id']}[/bold]\n"
            f"Type: {data['memory_type']} | Importance: {data['importance']}\n"
            f"Tags: {', '.join(data.get('tags', []))}",
            title="Memory Added",
        ))


@memory.command("get")
@click.argument("memory_id")
@click.pass_context
def memory_get(ctx: click.Context, memory_id: str):
    """Get a memory by ID"""
    with _get_client() as client:
        response = client.get(f"/api/v1/memory/{memory_id}")
        data = response.json()

        table = Table(title=f"Memory: {data['id']}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        table.add_row("Content", data["content"])
        table.add_row("Type", data["memory_type"])
        table.add_row("Importance", data["importance"])
        table.add_row("Tags", ", ".join(data.get("tags", [])))
        table.add_row("Created", data.get("created_at", "N/A"))

        console.print(table)


@memory.command("search")
@click.argument("query")
@click.option("--limit", "-n", default=5, help="Max results")
@click.option("--type", "memory_type", default=None, help="Filter by type")
@click.pass_context
def memory_search(ctx: click.Context, query: str, limit: int, memory_type: Optional[str]):
    """Search memories"""
    payload = {
        "query": query,
        "top_k": limit,
    }
    if memory_type:
        payload["memory_type"] = memory_type

    with _get_client() as client:
        response = client.post("/api/v1/memory/search", json=payload)
        data = response.json()

        results = data.get("results", [])
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("#", style="dim")
        table.add_column("Score", style="green")
        table.add_column("Content")
        table.add_column("Type")

        for i, r in enumerate(results, 1):
            table.add_row(
                str(i),
                f"{r['score']:.2f}",
                r["memory"]["content"][:80] + ("..." if len(r["memory"]["content"]) > 80 else ""),
                r["memory"]["memory_type"],
            )

        console.print(table)


@memory.command("list")
@click.option("--type", "memory_type", default=None, help="Filter by type")
@click.option("--limit", "-n", default=20, help="Max results")
@click.pass_context
def memory_list(ctx: click.Context, memory_type: Optional[str], limit: int):
    """List memories"""
    params = {"limit": limit}
    if memory_type:
        params["memory_type"] = memory_type

    with _get_client() as client:
        response = client.get("/api/v1/memory", params=params)
        data = response.json()

        memories = data.get("memories", [])
        if not memories:
            console.print("[yellow]No memories found[/yellow]")
            return

        table = Table(title="Memories")
        table.add_column("ID", style="cyan")
        table.add_column("Content")
        table.add_column("Type")
        table.add_column("Importance")

        for m in memories:
            content = m["content"][:60] + ("..." if len(m["content"]) > 60 else "")
            table.add_row(m["id"], content, m["memory_type"], m["importance"])

        console.print(table)


@memory.command("delete")
@click.argument("memory_id")
@click.confirmation_option(prompt="Are you sure you want to delete this memory?")
@click.pass_context
def memory_delete(ctx: click.Context, memory_id: str):
    """Delete a memory"""
    with _get_client() as client:
        response = client.delete(f"/api/v1/memory/{memory_id}")
        if response.status_code == 200:
            console.print(f"[green]✓[/green] Memory {memory_id} deleted")
        else:
            console.print(f"[red]✗[/red] Failed to delete memory")


# --- Search Commands ---

@cli.group()
def search():
    """Search operations"""
    pass


@search.command("web")
@click.argument("query")
@click.option("--limit", "-n", default=5, help="Max results")
@click.pass_context
def search_web(ctx: click.Context, query: str, limit: int):
    """Web search"""
    with _get_client() as client:
        response = client.post("/api/v1/search/web", json={"query": query, "max_results": limit})
        data = response.json()

        results = data.get("results", [])
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        for i, r in enumerate(results, 1):
            console.print(f"\n[bold cyan]{i}. {r['title']}[/bold cyan]")
            console.print(f"   [link={r['url']}]{r['url']}[/link]")
            console.print(f"   {r['snippet'][:120]}...")


@search.command("internal")
@click.argument("query")
@click.option("--limit", "-n", default=10, help="Max results")
@click.pass_context
def search_internal(ctx: click.Context, query: str, limit: int):
    """Internal hybrid search"""
    with _get_client() as client:
        response = client.post("/api/v1/search/internal", json={"query": query, "top_k": limit})
        data = response.json()

        results = data.get("results", [])
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(title=f"Internal Search: '{query}'")
        table.add_column("#", style="dim")
        table.add_column("Score", style="green")
        table.add_column("Title")
        table.add_column("URL")

        for i, r in enumerate(results, 1):
            table.add_row(str(i), f"{r.get('score', 0):.2f}", r["title"], r["url"])

        console.print(table)


# --- Crawl Commands ---

@cli.group()
def crawl():
    """Web crawl operations"""
    pass


@crawl.command("scrape")
@click.argument("url")
@click.pass_context
def crawl_scrape(ctx: click.Context, url: str):
    """Scrape a single URL"""
    with _get_client() as client:
        response = client.post("/api/v1/crawl/scrape", json={"url": url})
        data = response.json()

        console.print(Panel(
            f"[bold]{data.get('title', 'N/A')}[/bold]\n\n"
            f"{data['content'][:500]}{'...' if len(data['content']) > 500 else ''}",
            title=f"Scraped: {url}",
        ))


@crawl.command("map")
@click.argument("url")
@click.option("--limit", "-n", default=50, help="Max pages")
@click.pass_context
def crawl_map(ctx: click.Context, url: str, limit: int):
    """Map a website (get all URLs)"""
    with _get_client() as client:
        response = client.post("/api/v1/crawl/map", json={"url": url, "max_pages": limit})
        data = response.json()

        urls = data.get("urls", [])
        if not urls:
            console.print("[yellow]No URLs found[/yellow]")
            return

        console.print(f"[green]Found {len(urls)} URLs:[/green]")
        for u in urls[:limit]:
            console.print(f"  {u}")


# --- Knowledge Commands ---

@cli.group()
def knowledge():
    """Knowledge graph operations"""
    pass


@knowledge.command("create-entity")
@click.option("--name", "-n", required=True, help="Entity name")
@click.option("--type", "entity_type", default="concept", help="Entity type")
@click.option("--description", "-d", default=None, help="Description")
@click.pass_context
def knowledge_create_entity(ctx: click.Context, name: str, entity_type: str, description: Optional[str]):
    """Create a knowledge graph entity"""
    payload = {
        "name": name,
        "entity_type": entity_type,
    }
    if description:
        payload["description"] = description

    with _get_client() as client:
        response = client.post("/api/v1/knowledge/entities", json=payload)
        data = response.json()

        console.print(Panel(
            f"[green]✓[/green] Entity created: [bold]{data['id']}[/bold]\n"
            f"Name: {data['name']} | Type: {data['entity_type']}\n"
            f"Description: {data.get('description', 'N/A')}",
            title="Entity Created",
        ))


@knowledge.command("search")
@click.argument("query")
@click.option("--type", "entity_type", default=None, help="Filter by type")
@click.option("--limit", "-n", default=10, help="Max results")
@click.pass_context
def knowledge_search(ctx: click.Context, query: str, entity_type: Optional[str], limit: int):
    """Search entities"""
    payload = {"query": query, "top_k": limit}
    if entity_type:
        payload["entity_type"] = entity_type

    with _get_client() as client:
        response = client.post("/api/v1/knowledge/search", json=payload)
        data = response.json()

        entities = data.get("entities", [])
        if not entities:
            console.print("[yellow]No entities found[/yellow]")
            return

        table = Table(title=f"Entity Search: '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Type")
        table.add_column("Description")

        for e in entities:
            desc = (e.get("description") or "N/A")[:50]
            table.add_row(e["id"], e["name"], e["entity_type"], desc)

        console.print(table)


# --- Health Command ---

@cli.command()
def health():
    """Check API health"""
    with _get_client() as client:
        response = client.get("/api/v1/health")
        data = response.json()

        status_color = "green" if data.get("status") == "ok" else "red"
        console.print(Panel(
            f"Status: [{status_color}]{data.get('status', 'unknown')}[/{status_color}]\n"
            f"Version: {data.get('version', 'N/A')}\n"
            f"Services: {', '.join(data.get('services', {}).keys()) or 'N/A'}",
            title="API Health",
        ))


if __name__ == "__main__":
    cli()