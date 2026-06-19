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
      ],
    },
    {
      type: "category",
      label: "SDKs",
      items: [
        "sdk/python",
        "sdk/typescript",
      ],
    },
    {
      type: "doc",
      id: "cli",
      label: "CLI",
    },
    {
      type: "doc",
      id: "mcp",
      label: "MCP Server",
    },
    {
      type: "doc",
      id: "api-reference",
      label: "API Reference",
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
      id: "roadmap",
      label: "Roadmap",
    },
  ],
};

module.exports = sidebars;