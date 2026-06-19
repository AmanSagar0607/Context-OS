// @ts-check

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Context OS",
  tagline: "AI can finally remember — the open-source context infrastructure for AI agents.",
  favicon: "img/favicon.ico",
  url: "https://docs.context-ai.dev",
  baseUrl: "/",
  organizationName: "AmanSagar0607",
  projectName: "Context-OS",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: "./sidebars.js",
          editUrl: "https://github.com/AmanSagar0607/Context-OS/tree/main/docs/",
        },
        blog: {
          showReadingTime: true,
          editUrl: "https://github.com/AmanSagar0607/Context-OS/tree/main/docs/",
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: "img/social-card.png",
      navbar: {
        title: "Context OS",
        logo: {
          alt: "Context OS Logo",
          src: "img/logo.svg",
        },
        items: [
          {
            type: "docSidebar",
            sidebarId: "docsSidebar",
            position: "left",
            label: "Docs",
          },
          {
            to: "/docs/sdk/python",
            label: "SDK",
            position: "left",
          },
          {
            to: "/docs/api-reference",
            label: "API",
            position: "left",
          },
          {
            to: "/docs/mcp",
            label: "MCP",
            position: "left",
          },
          {
            to: "/blog",
            label: "Blog",
            position: "left",
          },
          {
            href: "https://discord.gg/YrSpR43UB",
            label: "Discord",
            position: "right",
          },
          {
            href: "https://github.com/AmanSagar0607/Context-OS",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Docs",
            items: [
              { label: "Quickstart", to: "/docs/getting-started" },
              { label: "Architecture", to: "/docs/architecture" },
              { label: "API Reference", to: "/docs/api-reference" },
            ],
          },
          {
            title: "SDKs",
            items: [
              { label: "Python SDK", to: "/docs/sdk/python" },
              { label: "TypeScript SDK", to: "/docs/sdk/typescript" },
              { label: "CLI", to: "/docs/cli" },
            ],
          },
          {
            title: "Community",
            items: [
              { label: "Discord", href: "https://discord.gg/YrSpR43UB" },
              { label: "Twitter", href: "https://x.com/AmanSagar0607a" },
              { label: "GitHub", href: "https://github.com/AmanSagar0607/Context-OS" },
            ],
          },
          {
            title: "More",
            items: [
              { label: "Blog", to: "/blog" },
              { label: "Roadmap", to: "/docs/roadmap" },
              { label: "Changelog", to: "/docs/changelog" },
            ],
          },
        ],
        copyright: `Copyright \u00A9 ${new Date().getFullYear()} Aman Sagar. Built with Docusaurus.`,
      },
      prism: {
        theme: require("prism-react-renderer").themes.github,
        darkTheme: require("prism-react-renderer").themes.dracula,
        additionalLanguages: ["bash", "json", "python", "typescript"],
      },
      colorMode: {
        defaultMode: "dark",
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

module.exports = config;