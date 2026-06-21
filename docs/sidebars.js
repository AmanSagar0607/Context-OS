/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    {
      type: "doc",
      id: "index",
      label: "Introduction",
    },
    {
      type: "doc",
      id: "getting-started",
      label: "Quickstart",
    },
    {
      type: "doc",
      id: "architecture",
      label: "Architecture",
    },
    {
      type: "category",
      label: "Core Concepts",
      items: [
        "concepts/memory",
        "concepts/retrieval",
        "concepts/knowledge-graph",
        "concepts/web-intelligence",
        "concepts/context-assembly",
        "concepts/agent-integration",
      ],
    },
    {
      type: "category",
      label: "Memory",
      items: [
        "memory/store",
        "memory/search",
        "memory/types",
        "memory/context-windows",
        "memory/consolidation",
        "memory/links",
        "memory/best-practices",
      ],
    },
    {
      type: "category",
      label: "Search",
      items: [
        "search/overview",
        "search/web",
      ],
    },
    {
      type: "category",
      label: "Crawl",
      items: [
        "crawl/overview",
        "crawl/scrape",
        "crawl/crawl",
        "crawl/map",
        "crawl/extract",
        "crawl/browser",
        "crawl/fallback",
      ],
    },
    {
      type: "category",
      label: "Knowledge",
      items: [
        "knowledge/overview",
        "knowledge/entities",
        "knowledge/relationships",
        "knowledge/graph-queries",
        "knowledge/auto-extraction",
      ],
    },
    {
      type: "category",
      label: "MCP",
      items: [
        "mcp/overview",
        "mcp/memory-mcp",
        "mcp/search-mcp",
        "mcp/crawl-mcp",
        "mcp/cursor-setup",
        "mcp/claude-setup",
      ],
    },
    {
      type: "category",
      label: "SDKs",
      items: [
        "sdk/python",
        "sdk/typescript",
        "sdk/go",
        "sdk/rust",
        "sdk/java",
      ],
    },
    {
      type: "doc",
      id: "cli/overview",
      label: "CLI",
    },
    {
      type: "doc",
      id: "api-reference",
      label: "API Reference",
    },
    {
      type: "category",
      label: "Guides",
      items: [
        "guides/agent-memory",
        "guides/hybrid-search",
        "guides/knowledge-patterns",
        "guides/migration-mem0",
        "guides/migration-firecrawl",
      ],
    },
    {
      type: "category",
      label: "Deployment",
      items: [
        "deployment/docker",
        "deployment/self-hosted",
      ],
    },
    {
      type: "doc",
      id: "examples",
      label: "Examples",
    },
    {
      type: "doc",
      id: "roadmap",
      label: "Roadmap",
    },
    {
      type: "doc",
      id: "changelog",
      label: "Changelog",
    },
  ],
};

module.exports = sidebars;
