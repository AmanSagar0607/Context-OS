"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { loadAuthUser } from "@/lib/auth";
import {
  ArrowRight,
  BookOpen,
  Bot,
  Brain,
  ChevronDown,
  CheckCircle2,
  Clock3,
  Code2,
  Database,
  FileText,
  GitBranch,
  Globe2,
  Layers,
  Lightbulb,
  MessageSquare,
  MousePointerClick,
  Search,
  Server,
  ShieldCheck,
  Star,
  Terminal,
  Users,
  Workflow,
  X,
  Zap,
} from "lucide-react";

import dynamic from "next/dynamic";
import { Skeleton } from "@/components/ui/skeleton";
import { AnimatedListItem } from "@/components/ui/animated-list";
import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { DottedMap } from "@/components/ui/dotted-map";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

const Globe = dynamic(() => import("@/components/ui/globe").then((m) => m.Globe), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center">
      <Skeleton className="h-[250px] w-[250px] rounded-full bg-[#f1e8dc]/60 dark:bg-slate-800/60" />
    </div>
  ),
});

const OrbitingCircles = dynamic(() => import("@/components/ui/orbiting-circles").then((m) => m.OrbitingCircles), {
  ssr: false,
  loading: () => <Skeleton className="h-[200px] w-[200px] rounded-full bg-[#f1e8dc]/40 dark:bg-slate-800/40" />,
});

const AnimatedList = dynamic(() => import("@/components/ui/animated-list").then((m) => m.AnimatedList), {
  ssr: false,
  loading: () => (
    <div className="mt-4 flex w-full flex-col gap-4">
      <Skeleton className="h-[68px] w-full rounded-[1rem] bg-[#f1e8dc]/60 dark:bg-slate-800/60" />
      <Skeleton className="h-[68px] w-full rounded-[1rem] bg-[#f1e8dc]/40 dark:bg-slate-800/40" />
      <Skeleton className="h-[68px] w-full rounded-[1rem] bg-[#f1e8dc]/20 dark:bg-slate-800/20" />
    </div>
  ),
});

const megaMenuItems = [
  { label: "Home", href: "#home" },
  {
    label: "Agent Flow",
    megaMenu: [
      {
        title: "Pipeline stages",
        items: [
          { label: "PDF Upload", href: "#agent-flow", desc: "Upload and process your documents" },
          { label: "Chunking", href: "#agent-flow", desc: "Split content into searchable pieces" },
          { label: "Memory", href: "#agent-flow", desc: "Persistent cross-session context" },
          { label: "Grounded Chat", href: "#agent-flow", desc: "Answers rooted in real sources" },
        ],
      },
      {
        title: "Capabilities",
        items: [
          { label: "Live Search", href: "#agent-flow", desc: "Web fallback when local context is not enough" },
          { label: "RAG Pipeline", href: "#agent-flow", desc: "Retrieval-augmented generation flow" },
          { label: "Session History", href: "#agent-flow", desc: "Browse past chats and artifacts" },
        ],
      },
    ],
  },
  {
    label: "Features",
    megaMenu: [
      {
        title: "Product",
        items: [
          { label: "Chat Workspace", href: "#features", desc: "AI-powered chat with memory" },
          { label: "PDF Analysis", href: "#features", desc: "Extract and query document content" },
          { label: "Artifact Storage", href: "#features", desc: "Save and organize your work" },
        ],
      },
      {
        title: "Integrations",
        items: [
          { label: "OpenRouter", href: "#features", desc: "Multi-model LLM gateway" },
          { label: "Vector Search", href: "#features", desc: "Milvus-powered similarity search" },
          { label: "PostgreSQL", href: "#features", desc: "Persistent user and session storage" },
        ],
      },
      {
        title: "Security",
        items: [
          { label: "Authentication", href: "#features", desc: "Email-based secure login" },
          { label: "Data Privacy", href: "#features", desc: "Your data stays yours" },
        ],
      },
    ],
  },
  {
    label: "Developers",
    megaMenu: [
      {
        title: "Stack",
        items: [
          { label: "Frontend", href: "#developers", desc: "Next.js, TypeScript, Magic UI" },
          { label: "Backend", href: "#developers", desc: "FastAPI, Python, async routes" },
          { label: "Infrastructure", href: "#developers", desc: "Docker, pgAdmin, health checks" },
        ],
      },
      {
        title: "Resources",
        items: [
          { label: "API Reference", href: "#developers", desc: "REST endpoints and schemas" },
          { label: "SDKs & Tools", href: "#developers", desc: "CLI, MCP Server, SDKs" },
          { label: "Changelog", href: "#developers", desc: "Latest updates and releases" },
        ],
      },
    ],
  },
  { label: "Pricing", href: "#pricing" },
];

const liveFeed = [
  {
    title: "Generating response...",
    description: "Synthesizing answer with verified citations.",
  },
  {
    title: "Web fallback initiated...",
    description: "Fetching live data to fill gaps in local context.",
  },
  {
    title: "Ranking grounded chunks...",
    description: "Prioritizing local artifact search over generic models.",
  },
  {
    title: "Checking persistent memory...",
    description: "Retrieving 3 past sessions and user context.",
  },
  {
    title: "Extracting document data...",
    description: "PDF parsing, chunking, and embedding generation.",
  },
];

const agentFlow = [
  "Sign up and start a chat workspace",
  "Upload a PDF and run the RAG pipeline",
  "Ask grounded questions with memory-aware context",
  "Review sources, status events, and saved history",
];

const developerCities = [
  { lat: 37.7749, lng: -122.4194, size: 0.7, pulse: true },
  { lat: 51.5072, lng: -0.1276, size: 0.7, pulse: true },
  { lat: 28.6139, lng: 77.209, size: 0.9, pulse: true },
  { lat: 19.076, lng: 72.8777, size: 0.7, pulse: true },
  { lat: 1.3521, lng: 103.8198, size: 0.7, pulse: true },
];

const pricingPlans = [
  {
    name: "Starter",
    price: "$0",
    period: "/ month",
    description: "For testing the chat workspace and PDF flows locally.",
    features: [
      "Email sign up and login",
      "PDF upload and basic RAG",
      "Recent chat history",
      "Local development setup",
    ],
  },
  {
    name: "Builder",
    price: "$19",
    period: "/ month",
    description: "For solo builders shipping a document-aware AI product.",
    features: [
      "Everything in Starter",
      "Persistent memory records",
      "Web fallback controls",
      "Postgres-backed sessions",
    ],
    featured: true,
  },
  {
    name: "Team",
    price: "Custom",
    period: "",
    description: "For teams that need agent governance and shared workflows.",
    features: [
      "Everything in Builder",
      "Shared workspaces",
      "Audit-friendly event traces",
      "Custom deployment support",
    ],
  },
];

const launchCards = [
  {
    title: "Search",
    description: "Search filings, market pages, research sources, and live sites with grounded retrieval built in.",
    Icon: Search,
  },
  {
    title: "Scrape",
    description: "Crawl finance and research sources first, then expand to any site that needs structured agent-ready data.",
    Icon: Layers,
    featured: true,
  },
  {
    title: "Interact",
    description: "Let agents inspect, click, retrieve, and operate across market, research, and general-purpose workflows.",
    Icon: MousePointerClick,
    badge: "New",
  },
];

const connectCards = [
  {
    title: "One command",
    description: "Connect finance, research, and document agents through CLI, docs, or MCP-style workflows in minutes.",
    code: "npx -y aman-crawl init --agent --browser",
    cta: "View setup docs",
  },
  {
    title: "Agent onboarding",
    description: "Fetch a starter skill, assign a model, and launch a focused market or research agent before expanding to broader crawl tasks.",
    code: "curl -s https://amanagent.dev/agent-onboarding/SKILL.md",
    cta: "Open onboarding guide",
  },
];

const performanceCards = [
  {
    eyebrow: "Reliable on any page",
    title: "Industry-grade coverage",
    text: "Handle finance docs, research pages, and dynamic web content with cleaner extractions and stronger downstream answers.",
    cta: "See benchmarks",
    Icon: ShieldCheck,
  },
  {
    eyebrow: "Speed that feels invisible",
    title: "Built for real-time agents",
    text: "Keep search, crawl, and scrape loops fast enough for live assistants and task-focused automation.",
    cta: "See comparisons",
    Icon: Clock3,
  },
  {
    eyebrow: "Docs to data",
    title: "Media parsing",
    text: "Parse PDFs and document-heavy sources so dedicated agents can reason over structured evidence instead of raw files.",
    Icon: BookOpen,
  },
  {
    eyebrow: "Knows the moment",
    title: "Smart wait",
    text: "Wait for the content that matters before extraction so results stay reliable on changing pages.",
    Icon: Lightbulb,
  },
  {
    eyebrow: "Advanced coverage",
    title: "Enhanced mode",
    text: "Reach tougher pages with better fallback coverage when standard browsing is not enough.",
    Icon: Globe2,
  },
  {
    eyebrow: "Interact with pages",
    title: "Agent actions",
    text: "Support click, type, scroll, wait, and inspect-style actions for supervised web workflows.",
    Icon: MousePointerClick,
  },
];

const useCases = [
  {
    title: "Finance research",
    description: "Build market-aware agents that gather filings, news, company pages, and analyst-style evidence with traceable context.",
  },
  {
    title: "Deep research",
    description: "Build research agents that gather sources, summarize evidence, and keep traceable context.",
  },
  {
    title: "Dedicated AI agents",
    description: "Create focused agents for finance, onboarding, specs, compliance, or support workflows before generalizing to anything else.",
  },
  {
    title: "Crawl anything",
    description: "Once the finance and research core is strong, expand the same pipeline to any live page, site, or document source.",
  },
];

const testimonials = [
  {
    name: "Indie builders",
    quote: "We can launch task-specific document agents without stitching five separate tools together.",
  },
  {
    name: "Research teams",
    quote: "Search plus crawl plus structured retrieval makes evidence-grounded workflows easier to trust.",
  },
  {
    name: "Product engineers",
    quote: "The page now feels closer to the actual product promise: agent-ready data and execution flow.",
  },
  {
    name: "Open-source users",
    quote: "The new surface communicates speed, control, and developer utility without losing the current app identity.",
  },
];

const faqs = [
  {
    question: "What is Aman Platform?",
    answer:
      "Aman Platform is a unified AI operating system combining persistent memory (AmanAgentLab) with web intelligence infrastructure (AmanCrawl). It helps users remember everything, understand context, and automate work.",
  },
  {
    question: "What does AmanAgentLab do?",
    answer:
      "AmanAgentLab is the personal AI workspace layer — memory, artifacts, RAG, knowledge workspace, and agent workflows. It remembers what you've worked on and helps you get work done.",
  },
  {
    question: "What does AmanCrawl do?",
    answer:
      "AmanCrawl is the web intelligence layer — search, crawl, scrape, and extract structured data from any website. It powers AI agents with clean, structured web data.",
  },
  {
    question: "How does the search flow work?",
    answer:
      "The agent checks recent conversation context, uploaded artifacts, saved memory, and only then falls back to live web search when local context is not enough.",
  },
  {
    question: "Can I use my own PDFs and knowledge sources?",
    answer:
      "Yes. The platform supports PDF upload, extraction, chunking, embeddings, vector storage, and grounded chat against processed documents.",
  },
  {
    question: "What stack powers the platform?",
    answer:
      "Aman Platform uses Next.js, FastAPI, OpenRouter, Milvus or Zilliz Cloud, PostgreSQL, Docker, TypeScript, and AG-UI shaped server events.",
  },
];

const pipelineNodes = [
  { id: "pdf",    label: "PDF Upload",   sub: "42 pages",        Icon: FileText,      delay: 0    },
  { id: "chunk",  label: "Chunker",      sub: "128 chunks",      Icon: Layers,        delay: 0.15 },
  { id: "memory", label: "Memory",       sub: "Context loaded",  Icon: Brain,         delay: 0.3  },
  { id: "chat",   label: "Chat",         sub: "Grounded reply",  Icon: MessageSquare, delay: 0.45 },
];

function PipelineFlow() {
  return (
    <div className="relative flex h-full w-full items-center justify-center gap-0 px-4">
      {pipelineNodes.map((node, i) => (
        <div key={node.id} className="flex items-center">
          {/* Node */}
          <motion.div
            initial={{ opacity: 0, scale: 0.82 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.45, delay: node.delay, ease: [0.22, 1, 0.36, 1] }}
            className="relative flex flex-col items-center gap-2"
          >
            {/* Socket top */}
            {i > 0 && (
              <div className="absolute -left-1.5 top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full border-2 border-[#fa5a19] bg-white dark:bg-slate-900" />
            )}
            {i < pipelineNodes.length - 1 && (
              <div className="absolute -right-1.5 top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full border-2 border-[#fa5a19] bg-[#fa5a19]" />
            )}

            {/* Card */}
            <div className="flex w-[124px] flex-col items-center gap-1.5 rounded-[1.25rem] border border-[#e5e7eb] bg-white/95 p-4 shadow-[0_8px_30px_rgba(64,43,24,0.06)] backdrop-blur dark:border-white/10 dark:bg-slate-950/80">
              <div className="flex h-11 w-11 items-center justify-center rounded-[0.85rem] border border-[#e5e7eb] bg-gradient-to-br from-white to-[#f5f5f5] shadow-[0_2px_10px_rgba(230,125,43,0.08)] dark:border-white/10 dark:from-slate-900 dark:to-slate-800">
                <node.Icon className="h-[22px] w-[22px] text-[#fa5a19]" strokeWidth={1.75} />
              </div>
              <div className="mt-1.5 flex flex-col items-center">
                <p className="text-center text-[12px] font-semibold leading-tight text-[#262626] dark:text-white">{node.label}</p>
                <p className="mt-1 text-center text-[11px] leading-tight text-[#666666]">{node.sub}</p>
              </div>
              {/* Status dot */}
              <span className="mt-1.5 flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-1.5 w-1.5 animate-ping rounded-full bg-[#fa5a19] opacity-60" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-[#fa5a19]" />
              </span>
            </div>
          </motion.div>

          {/* Connector line between nodes */}
          {i < pipelineNodes.length - 1 && (
            <div className="relative mx-1.5 flex h-6 w-12 items-center lg:w-16">
              <svg viewBox="0 0 64 8" className="w-full" preserveAspectRatio="none">
                {/* Track */}
                <line x1="0" y1="4" x2="64" y2="4" stroke="#e5d8c9" strokeWidth="1.5" className="dark:stroke-white/10" />
                {/* Animated travelling dash */}
                <motion.line
                  x1="0" y1="4" x2="64" y2="4"
                  stroke="#fa5a19"
                  strokeWidth="1.5"
                  strokeDasharray="8 6"
                  initial={{ strokeDashoffset: 28 }}
                  animate={{ strokeDashoffset: -28 }}
                  transition={{
                    duration: 1.2,
                    repeat: Infinity,
                    ease: "linear",
                    delay: node.delay + 0.3,
                  }}
                />
                {/* Arrowhead */}
                <polygon points="60,1.5 64,4 60,6.5" fill="#fa5a19" />
              </svg>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

const bentoItems = [
  {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    Icon: (() => null) as any,
    name: "Upload PDFs and run RAG pipelines",
    description:
      "Upload documents, trigger extraction and chunking, then chat against grounded context.",
    href: "/chat",
    cta: "Open chat",
    className: "lg:col-span-2",
    background: (
      <div className="absolute inset-0 overflow-hidden bg-[radial-gradient(circle_at_80%_10%,rgba(230,125,43,0.10),transparent_30%),linear-gradient(180deg,white_0%,#f7f2ea_100%)] dark:bg-[radial-gradient(circle_at_80%_10%,rgba(230,125,43,0.18),transparent_34%),linear-gradient(180deg,#3a2c24_0%,#241a15_100%)]">
        <div className="absolute inset-x-0 top-4 bottom-[8rem]">
          <PipelineFlow />
        </div>
      </div>
    ),
  },
  {
    name: "Visible search hierarchy",
    description:
      "The app reveals when it is checking memory, artifacts, or web fallback so users understand how the answer was assembled.",
    href: "#agent-flow",
    cta: "See flow",
    className: "lg:col-span-1",
      background: (
      <div className="absolute inset-0 overflow-hidden bg-[radial-gradient(circle_at_top,rgba(230,125,43,0.16),transparent_42%),linear-gradient(180deg,white_0%,#f7f2ea_100%)] dark:bg-[radial-gradient(circle_at_top,rgba(230,125,43,0.18),transparent_44%),linear-gradient(180deg,#3a2b23_0%,#241915_100%)]">
        <div className="absolute inset-x-0 top-0 bottom-24 overflow-hidden px-6 pt-6">
          <AnimatedList delay={1500} className="mt-4 items-stretch">
            {liveFeed.map((item) => (
              <AnimatedListItem key={item.title}>
                <div className="career-muted-card rounded-[1rem] border border-[#e5e7eb] p-3 text-left dark:border-white/10 dark:bg-slate-900/60">
                  <div className="text-[13px] font-semibold text-[#262626] dark:text-white">
                    {item.title}
                  </div>
                  <p className="mt-1.5 text-xs leading-tight text-[#666666]">
                    {item.description}
                  </p>
                </div>
              </AnimatedListItem>
            ))}
          </AnimatedList>
        </div>
      </div>
    ),
  },
  {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    Icon: (() => null) as any,
    name: "Global integrations",
    description: "Models, storage, and live search — one loop.",
    href: "#developers",
    cta: "View stack",
    className: "lg:col-span-1",
    background: (
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden bg-[linear-gradient(180deg,white_0%,#f7f2ea_100%)] dark:bg-[linear-gradient(180deg,#382922_0%,#231915_100%)]">
        <Globe className="scale-[1.1]" />
      </div>
    ),
  },
  {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    Icon: (() => null) as any,
    name: "Seamless integrations",
    description: "Effortlessly integrate models, storage, databases, and live search services into one streamlined agent loop.",
    href: "#developers",
    cta: "View stack",
    className: "lg:col-span-2",
    background: (
      <div className="absolute inset-0 overflow-hidden bg-[radial-gradient(circle_at_80%_50%,rgba(230,125,43,0.06),transparent_40%),linear-gradient(180deg,white_0%,#f7f2ea_100%)] dark:bg-[radial-gradient(circle_at_80%_50%,rgba(230,125,43,0.12),transparent_42%),linear-gradient(180deg,#382922_0%,#221814_100%)]">
        <div className="absolute -right-[10%] top-1/2 flex h-[500px] w-[500px] -translate-y-1/2 items-center justify-center lg:-right-[5%] lg:h-[600px] lg:w-[600px]">
          {/* Inner Circle */}
          <OrbitingCircles radius={80} duration={20} iconSize={40}>
            <div className="flex h-10 w-10 items-center justify-center rounded-[8px] border border-[#e5e7eb] bg-white shadow-[color(display-p3_0.9804_0.3647_0.098/0.06)_0px_1px_1px_0px] dark:border-white/10 dark:bg-[#262626]">
              <Database className="h-[18px] w-[18px] text-[#fa5a19]" />
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-[8px] border border-[#e5e7eb] bg-white shadow-[color(display-p3_0.9804_0.3647_0.098/0.06)_0px_1px_1px_0px] dark:border-white/10 dark:bg-[#262626]">
              <Server className="h-[18px] w-[18px] text-[#fa5a19]" />
            </div>
          </OrbitingCircles>
          {/* Outer Circle */}
          <OrbitingCircles radius={150} duration={25} reverse iconSize={40}>
            <div className="flex h-10 w-10 items-center justify-center rounded-[8px] border border-[#e5e7eb] bg-white shadow-[color(display-p3_0.9804_0.3647_0.098/0.06)_0px_1px_1px_0px] dark:border-white/10 dark:bg-[#262626]">
              <Globe2 className="h-[18px] w-[18px] text-[#fa5a19]" />
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-[8px] border border-[#e5e7eb] bg-white shadow-[color(display-p3_0.9804_0.3647_0.098/0.06)_0px_1px_1px_0px] dark:border-white/10 dark:bg-[#262626]">
              <Workflow className="h-[18px] w-[18px] text-[#fa5a19]" />
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-[8px] border border-[#e5e7eb] bg-white shadow-[color(display-p3_0.9804_0.3647_0.098/0.06)_0px_1px_1px_0px] dark:border-white/10 dark:bg-[#262626]">
              <Zap className="h-[18px] w-[18px] text-[#fa5a19]" />
            </div>
          </OrbitingCircles>
        </div>
      </div>
    ),
  },

];

const surfaces = [
  {
    title: "CLI",
    text: "Terminal-first interface for memory, search, and agent actions.",
    Icon: Terminal,
    num: "01",
  },
  {
    title: "Web Browser",
    text: "Live preview URL for grounded navigation and visual workflows.",
    Icon: Globe2,
    num: "02",
  },
  {
    title: "MCP Server",
    text: "Connect tools and systems through a shared agent protocol layer.",
    Icon: Server,
    num: "03",
  },
  {
    title: "AI Agent",
    text: "Run supervised assistants and workflow-capable agent behavior.",
    Icon: Bot,
    num: "04",
  },
];

export default function Home() {
  const [isLoggedIn] = useState(() => loadAuthUser() !== null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [showPromoBanner, setShowPromoBanner] = useState(true);

  return (
    <main id="home" className="min-h-screen text-[#201510] dark:text-white">
      <div className="relative isolate">
        <div className="absolute inset-0 -z-30 firecrawl-shell" />
        <div className="absolute inset-0 -z-20 firecrawl-grid opacity-60" />

        {/* ── Hero ─────────────────────────────────────────────────────── */}
        <section className="px-5 pt-4 pb-10 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            {showPromoBanner ? (
              <div className="mb-4 flex justify-center">
              <div className="relative w-full max-w-[1056px]">
              <Link
                href={isLoggedIn ? "/chat" : "/signup"}
                className="inline-flex min-h-11 w-full items-center justify-center rounded-full bg-[#fa5a19] px-12 text-center text-[14px] font-medium text-white transition hover:bg-[#e04a10] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#fa5a19]/40"
              >
                Introducing AmanCrawl. Crawl the web, map pages, and turn sites into agent-ready data. Try it now →
              </Link>
              <button
                type="button"
                aria-label="Dismiss AmanCrawl announcement"
                onClick={() => setShowPromoBanner(false)}
                className="absolute right-3 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-white/80 transition hover:bg-white/12 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40"
              >
                <X className="h-4 w-4" />
              </button>
                </div>
              </div>
            ) : null}

            <header className="firecrawl-panel sticky top-4 z-50 flex items-center gap-4 rounded-full px-4 py-2.5 backdrop-blur" style={{ position: "relative" }}>
              <Link href="/" className="flex items-center gap-2.5">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#fa5a19] text-white shadow-[0_6px_14px_-8px_rgba(250,90,25,0.8)]">
                  <Zap className="h-3.5 w-3.5" />
                </span>
                <span className="text-[13px] font-semibold tracking-tight text-[#201510] dark:text-white">AmanAgent Lab</span>
              </Link>

              <nav className="hidden flex-1 items-center justify-center gap-6 text-[13px] font-medium text-[#666666] dark:text-white/70 md:flex">
                {megaMenuItems.map((item) => (
                  <MegaMenuItem
                    key={item.label}
                    item={item}
                    isOpen={activeMenu === item.label}
                    onOpen={() => setActiveMenu(item.label)}
                    onClose={() => setActiveMenu(null)}
                  />
                ))}
              </nav>

              <div className="ml-auto flex items-center gap-2">
                <AnimatedThemeToggler
                  className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#e5e7eb] bg-white text-[#666666] transition hover:border-[#fa5a19]/30 hover:text-[#201510] dark:border-white/10 dark:bg-transparent dark:text-white/70 dark:hover:border-white/20 dark:hover:text-white"
                  variant="circle"
                />
                {!isLoggedIn ? (
                  <Link
                    href="https://github.com"
                    target="_blank"
                    rel="noreferrer"
                    className="hidden sm:inline-flex min-h-11 items-center gap-2 rounded-full px-3 text-[13px] font-medium text-[#201510] transition hover:bg-[#fff2ea] dark:text-white/70 dark:hover:bg-white/5"
                  >
                    <GitBranch className="h-4 w-4" />
                    133.4K
                  </Link>
                ) : (
                  <Link
                    href="/chat"
                    className="hidden sm:inline-flex min-h-11 items-center gap-2 rounded-full px-3 text-[13px] font-medium text-[#201510] transition hover:bg-[#fff2ea] dark:text-white/70 dark:hover:bg-white/5"
                  >
                    <Zap className="h-4 w-4" />
                    Workspace
                  </Link>
                )}
                <Link href={isLoggedIn ? "/chat" : "/signup"} className="hidden sm:inline-flex">
                  <button className="inline-flex min-h-11 items-center justify-center rounded-full bg-[#fa5a19] px-5 text-[13px] font-semibold text-white transition hover:bg-[#e04a10] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#fa5a19]/40 active:bg-[#c93d0c]">
                    {isLoggedIn ? "Go to chat" : "Sign up"}
                  </button>
                </Link>
              </div>
            </header>

            <div className="firecrawl-panel relative mt-10 overflow-hidden rounded-[28px]">
              <div className="absolute inset-0 grainy-mesh-bg opacity-90 dark:opacity-50" />
              <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(255,253,250,0.72),rgba(247,242,234,0.76))] dark:bg-[linear-gradient(180deg,rgba(0,0,0,0.72),rgba(9,9,9,0.78))]" />
              <div className="absolute inset-0 firecrawl-grid opacity-[0.08] dark:opacity-[0.04]" />
              <div className="relative px-6 py-12 sm:px-8 lg:px-12">
                <div className="grid gap-10 lg:grid-cols-[1.02fr_0.98fr] lg:items-start">
                  <div className="max-w-[42rem] dark:max-w-[48rem]">
                    <div className="firecrawl-display text-balance text-[3.2rem] leading-[0.92] text-[#201510] sm:text-[4.4rem] lg:text-[5.6rem] dark:text-white">
                      One platform.
                      <br />
                      Two products.
                      <br />
                      <span className="text-[#fa5a19]">Your AI operating system.</span>
                    </div>

                    <p className="mt-6 max-w-xl text-[1rem] leading-7 text-[#666666] sm:text-[1.05rem] dark:text-white/70">
                      Aman Platform unifies persistent memory, agent workflows, and web intelligence.
                      AmanAgentLab remembers your context. AmanCrawl turns the web into agent-ready data.
                    </p>

                    <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
                      <Link
                        href="/chat"
                        className="inline-flex items-center justify-center rounded-full bg-[#fa5a19] px-6 py-3 text-[15px] font-semibold text-white transition hover:bg-[#e04a10] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#fa5a19]/40 active:bg-[#c93d0c]"
                      >
                        Explore AmanAgentLab
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                      <Link
                        href="/amancrawl"
                        className="inline-flex items-center justify-center rounded-full border border-[#e5e7eb] bg-white px-6 py-3 text-[15px] font-medium text-[#201510] transition hover:bg-[#f7f2ea] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#fa5a19]/40 dark:border-white/10 dark:bg-transparent dark:text-white dark:hover:bg-white/5"
                      >
                        Explore AmanCrawl
                      </Link>
                    </div>
                  </div>

                  <div className="relative min-h-[28rem]">
                    <div className="career-sun absolute right-[4%] top-0 h-[17rem] w-[17rem] rounded-[32px] opacity-95 sm:h-[20rem] sm:w-[20rem] lg:right-[2%] lg:h-[21rem] lg:w-[21rem]" />

                    <div className="relative ml-auto mt-24 max-w-[34rem]">
                      {/* AmanCrawl card */}
                      <div className="firecrawl-card rounded-[28px] p-3 shadow-[0_24px_60px_-30px_rgba(0,0,0,0.24)] dark:bg-white/5">
                        <div className="rounded-[22px] border border-[#e5e7eb] bg-white/95 p-3 dark:border-white/10 dark:bg-black/30">
                          <div className="flex items-center gap-2 rounded-[18px] border border-[#e5e7eb] bg-[#faf7f2] px-4 py-3 dark:border-white/10 dark:bg-white/5">
                            <Globe2 className="h-4 w-4 text-[#a18672] dark:text-white/50" />
                            <span className="text-sm text-[#8a8177] dark:text-white/50">https://example.com</span>
                          </div>

                          <div className="mt-3 flex items-center gap-2">
                            {["Search", "Scrape", "Map", "Crawl"].map((tab) => (
                              <span
                                key={tab}
                                className={`rounded-full px-3 py-2 text-sm ${
                                  tab === "Scrape"
                                    ? "bg-[#fff2ea] text-[#201510]"
                                    : "bg-[#f3eee7] text-[#8a8177] dark:bg-white/5 dark:text-white/50"
                                }`}
                              >
                                {tab}
                              </span>
                            ))}
                            <span className="ml-auto flex h-9 w-9 items-center justify-center rounded-[14px] bg-[#fa5a19] text-white">
                              <ArrowRight className="h-4 w-4" />
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Two product cards */}
                      <div className="mt-5 grid gap-4 md:grid-cols-2">
                        <div className="firecrawl-card rounded-[22px] p-4 dark:bg-white/5">
                          <div className="flex items-center gap-2">
                            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#fa5a19] text-white">
                              <Brain className="h-3 w-3" />
                            </span>
                            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#a18672] dark:text-white/50">
                              AmanAgentLab
                            </p>
                          </div>
                          <p className="mt-2 text-sm leading-6 text-[#666666] dark:text-white/70">
                            Memory, artifacts, and context — your personal AI operating system.
                          </p>
                        </div>
                        <div className="firecrawl-card rounded-[22px] p-4 dark:bg-white/5">
                          <div className="flex items-center gap-2">
                            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#fa5a19] text-white">
                              <Search className="h-3 w-3" />
                            </span>
                            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#a18672] dark:text-white/50">
                              AmanCrawl
                            </p>
                          </div>
                          <p className="mt-2 text-sm leading-6 text-[#666666] dark:text-white/70">
                            Search, crawl, and scrape — web intelligence for AI agents.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Available surfaces ───────────────────────────────────────── */}
        <section className="px-5 pb-20 pt-6 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            {/* Ruled label */}
            <div className="mb-10 flex items-center gap-4">
              <span className="h-px flex-1 bg-[#e5e7eb] dark:bg-white/10" />
              <p className="firecrawl-kicker text-[10px] font-semibold tracking-[0.28em]">
                Available surfaces
              </p>
              <span className="h-px flex-1 bg-[#e5e7eb] dark:bg-white/10" />
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {surfaces.map((item) => (
                <div
                  key={item.title}
                  className="group firecrawl-card relative overflow-hidden rounded-[20px] px-6 py-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-[#fa5a19]/25 hover:shadow-[0_18px_42px_-30px_rgba(0,0,0,0.24)] dark:border-white/10 dark:bg-white/5 dark:shadow-none"
                >
                  {/* Watermark number */}
                  <span className="pointer-events-none absolute right-5 top-4 select-none font-mono text-[3rem] font-bold leading-none text-[#e5e7eb] dark:text-white/10">
                    {item.num}
                  </span>

                  {/* Icon */}
                  <div className="relative mb-5 flex h-12 w-12 items-center justify-center rounded-[12px] border border-[#e5e7eb] bg-gradient-to-br from-white to-[#f5f5f5] shadow-[0_1px_1px_rgba(15,23,42,0.04)] dark:border-white/10 dark:from-white/5 dark:to-white/5">
                    <item.Icon className="h-5 w-5 text-[#fa5a19]" />
                  </div>

                  <h3 className="text-sm font-semibold tracking-[-0.01em] text-[#201510] dark:text-white">
                    {item.title}
                  </h3>
                  <p className="mt-2.5 text-sm leading-6 text-[#666666] dark:text-white/70">
                    {item.text}
                  </p>

                  {/* Hover accent line */}
                  <span className="absolute bottom-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-[#fa5a19]/35 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Two Products ─────────────────────────────────────────────── */}
        <section id="platform" className="px-5 py-20 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            <SectionHeading
              eyebrow="One platform, two products"
              title="Memory meets web intelligence"
              text="Aman Platform combines persistent memory with web intelligence — giving you a complete AI operating system."
            />

            <div className="mt-12 grid gap-6 lg:grid-cols-2">
              {/* AmanAgentLab */}
              <div id="agentlab" className="firecrawl-card group relative overflow-hidden rounded-[24px] p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_60px_-30px_rgba(250,90,25,0.2)]">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(250,90,25,0.08),transparent_40%)] dark:bg-[radial-gradient(circle_at_20%_20%,rgba(250,90,25,0.12),transparent_40%)]" />
                <div className="relative">
                  <div className="mb-6 flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#fa5a19] text-white">
                      <Brain className="h-5 w-5" />
                    </span>
                    <div>
                      <h3 className="text-xl font-semibold text-[#201510] dark:text-white">AmanAgentLab</h3>
                      <p className="text-xs text-[#666666] dark:text-white/50">Personal AI Operating System</p>
                    </div>
                  </div>

                  <p className="mb-6 max-w-md text-sm leading-7 text-[#666666] dark:text-white/70">
                    Remember everything. Understand context. Help users get work done.
                    Your AI workspace with persistent memory, artifacts, and agent workflows.
                  </p>

                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { icon: Brain, label: "Memory", desc: "Long-term persistent context" },
                      { icon: FileText, label: "Artifacts", desc: "Documents, notes, and work" },
                      { icon: Database, label: "RAG", desc: "Retrieval-augmented generation" },
                      { icon: Bot, label: "Agents", desc: "Research and automation workflows" },
                    ].map((item) => (
                      <div key={item.label} className="flex items-start gap-3 rounded-[12px] bg-white/60 p-3 dark:bg-white/5">
                        <item.icon className="mt-0.5 h-4 w-4 shrink-0 text-[#fa5a19]" />
                        <div>
                          <p className="text-xs font-semibold text-[#201510] dark:text-white">{item.label}</p>
                          <p className="text-[11px] text-[#666666] dark:text-white/50">{item.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <Link
                    href="/chat"
                    className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-[#fa5a19] transition hover:text-[#e04a10]"
                  >
                    Explore AmanAgentLab
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>

              {/* AmanCrawl */}
              <div id="amancrawl" className="firecrawl-card group relative overflow-hidden rounded-[24px] p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_60px_-30px_rgba(250,90,25,0.2)]">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(250,90,25,0.08),transparent_40%)] dark:bg-[radial-gradient(circle_at_80%_20%,rgba(250,90,25,0.12),transparent_40%)]" />
                <div className="relative">
                  <div className="mb-6 flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#fa5a19] text-white">
                      <Globe2 className="h-5 w-5" />
                    </span>
                    <div>
                      <h3 className="text-xl font-semibold text-[#201510] dark:text-white">AmanCrawl</h3>
                      <p className="text-xs text-[#666666] dark:text-white/50">Web Intelligence Infrastructure</p>
                    </div>
                  </div>

                  <p className="mb-6 max-w-md text-sm leading-7 text-[#666666] dark:text-white/70">
                    Turn websites into AI-ready data. Search, crawl, scrape, and extract
                    structured information at scale for your AI agents.
                  </p>

                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { icon: Search, label: "Search", desc: "Find and discover web content" },
                      { icon: Globe2, label: "Crawl", desc: "Intelligent site crawling" },
                      { icon: FileText, label: "Extract", desc: "Structured data extraction" },
                      { icon: Terminal, label: "API & CLI", desc: "REST, SDK, and MCP integration" },
                    ].map((item) => (
                      <div key={item.label} className="flex items-start gap-3 rounded-[12px] bg-white/60 p-3 dark:bg-white/5">
                        <item.icon className="mt-0.5 h-4 w-4 shrink-0 text-[#fa5a19]" />
                        <div>
                          <p className="text-xs font-semibold text-[#201510] dark:text-white">{item.label}</p>
                          <p className="text-[11px] text-[#666666] dark:text-white/50">{item.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <Link
                    href="/amancrawl"
                    className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-[#fa5a19] transition hover:text-[#e04a10]"
                  >
                    Explore AmanCrawl
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Quote ────────────────────────────────────────────────────── */}
        <section className="px-5 pb-18 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-3xl text-center">
            <p className="career-quote text-balance text-3xl font-medium leading-tight tracking-[-0.05em] sm:text-4xl">
              {"\""} A platform should be useful before it is flashy.
              <br />
              <span className="career-orange">Aman Platform</span> keeps the work grounded.{"\""}
            </p>
            <div className="mt-6 flex items-center justify-center gap-3 text-xs text-[#666666]">
                  <span className="h-8 w-8 rounded-full bg-[linear-gradient(135deg,#fa5a19,#f5c083)]" />
              <span>Built for developers, researchers, and knowledge workers</span>
            </div>
          </div>
        </section>

        {/* ── Features bento ───────────────────────────────────────────── */}
        <section id="features" className="career-section px-5 py-20 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            <SectionHeading
              eyebrow="Platform capabilities"
              title="Everything you need, already wired in"
              text="Memory, agents, web intelligence, and context retrieval — all connected in one platform loop."
            />

            <div className="mt-12">
              <BentoGrid className="grid-cols-1 auto-rows-[26rem] lg:grid-cols-3">
                {bentoItems.map((item) => (
                  <BentoCard key={item.name} {...item} />
                ))}
              </BentoGrid>
            </div>
          </div>
        </section>

        {/* ── Agent flow ───────────────────────────────────────────────── */}
        <section id="agent-flow" className="career-section-clean px-5 py-18 sm:px-8 lg:px-12">
          <div className="mx-auto grid max-w-[1216px] gap-8 lg:grid-cols-[0.92fr_1.08fr]">
            <div className="career-card rounded-[2rem] p-6 dark:border-white/10 dark:bg-slate-950/70">
              <p className="career-eyebrow text-xs font-semibold">
                Agent workflow
              </p>
              <h2 className="career-display mt-4 text-3xl font-semibold tracking-[-0.04em] text-[#262626] dark:text-white">
                A clear path from upload to answer
              </h2>
              <div className="mt-8 space-y-4">
                {agentFlow.map((step, index) => (
                  <div
                    key={step}
                    className="career-muted-card rounded-[1.5rem] p-4 dark:border-white/10 dark:bg-slate-900/70"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-[#262626] dark:text-white">
                        {step}
                      </p>
                      <span className="rounded-full border border-[#e5e7eb] bg-white/76 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#fa5a19] dark:border-white/10 dark:bg-[#262626] dark:text-[#fa5a19]">
                        Step {index + 1}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="career-card-dark relative overflow-hidden rounded-[2rem] p-6 text-white dark:border-white/10">
              <div className="career-dot-field absolute inset-0 opacity-20" />
              <div className="relative">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/60">
                  Live event stream
                </p>
                <h3 className="career-display mt-4 text-3xl font-semibold tracking-[-0.04em]">
                  The app shows what the agent is doing
                </h3>
                <p className="mt-4 max-w-xl text-sm leading-7 text-white/70">
                  AG-UI shaped server events make the product feel observable:
                  searching memory, searching artifacts, generating an answer,
                  or reporting an error never happens silently.
                </p>
                <div className="mt-8 grid gap-3">
                  {liveFeed.map((item) => (
                    <div
                      key={item.title}
                      className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
                    >
                      <div className="flex items-center gap-2 text-sm font-semibold text-white">
                        <span className="h-2.5 w-2.5 rounded-full bg-[#fa5a19]" />
                        {item.title}
                      </div>
                      <p className="mt-2 text-sm leading-6 text-white/70">
                        {item.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Developers ───────────────────────────────────────────────── */}
        <section id="developers" className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="career-card mx-auto max-w-[1216px] overflow-hidden rounded-[2rem] dark:border-white/10 dark:bg-slate-950/70">
            <div className="relative grid gap-8 p-6 lg:grid-cols-[1fr_0.9fr] lg:p-10">
              <div className="absolute inset-0 opacity-60">
                <FlickeringGrid
                  squareSize={3}
                  gridGap={8}
                  color="rgb(230,125,43)"
                  maxOpacity={0.12}
                  className="h-full w-full"
                />
              </div>
              <div className="relative">
                <SectionHeading
                  align="left"
                  eyebrow="Developer-ready"
                  title="Built for builders shipping real agent products"
                  text="Below the marketing layer, Aman Platform already has the core developer stack needed for a practical AI application with memory, agents, and web intelligence."
                />
                <div className="mt-8 grid gap-3 sm:grid-cols-2">
                  {[
                    {
                      title: "Frontend",
                      text: "Next.js app router, TypeScript, and a growing Magic UI based interface.",
                    },
                    {
                      title: "Backend",
                      text: "FastAPI routes for auth, upload, chat, health, and pipeline execution.",
                    },
                    {
                      title: "Data layer",
                      text: "Milvus or Zilliz for vectors, PostgreSQL for users, sessions, conversations, and memory.",
                    },
                    {
                      title: "Ops flow",
                      text: "Docker, pgAdmin, health checks, and env-driven local versus containerized modes.",
                    },
                  ].map((item) => (
                    <div
                      key={item.title}
                      className="career-muted-card rounded-[1.5rem] p-4 dark:border-white/10 dark:bg-slate-900/80"
                    >
                      <p className="text-sm font-semibold text-[#262626] dark:text-white">
                        {item.title}
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[#666666] dark:text-white/70">
                        {item.text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="relative min-h-[26rem] overflow-hidden rounded-[1.75rem] border border-[#e5e7eb] bg-[linear-gradient(180deg,white_0%,#f1e8dc_100%)] p-6 dark:border-white/10 dark:bg-[linear-gradient(180deg,#0f172a_0%,#111827_100%)]">
                <div className="absolute inset-0">
                  <DottedMap
                    markers={developerCities}
                    dotColor="rgba(148,163,184,0.6)"
                    markerColor="#fa5a19"
                    className="h-full w-full"
                    pulse
                  />
                </div>
                <div className="relative flex h-full flex-col justify-between">
                  <div>
                    <p className="career-eyebrow text-xs font-semibold">
                      Teams and developers
                    </p>
                    <h3 className="career-display mt-4 max-w-sm text-2xl font-semibold tracking-[-0.04em] text-[#262626] dark:text-white">
                      Ship to users, then keep improving the agent loop
                    </h3>
                  </div>
                  <div className="career-muted-card rounded-[1.5rem] p-5 backdrop-blur dark:border-white/10 dark:bg-slate-900/85">
                    <p className="text-sm leading-7 text-[#666666] dark:text-white/70">
                      From authentication to retrieval to developer operations,
                      the current app is already shaped like a product platform,
                      not just a one-screen chat demo.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pricing ──────────────────────────────────────────────────── */}
        <section className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            <SectionHeading
              eyebrow="Developer first"
              title="Start scraping today"
              text="Start with finance and research crawling, then extend the same platform to any site, source, or workflow."
            />
            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              {launchCards.map((card) => (
                <article
                  key={card.title}
                  className={`firecrawl-card rounded-[22px] p-6 text-center ${
                    card.featured ? "ring-1 ring-[#fa5a19]/25 shadow-[0_18px_40px_-28px_rgba(250,90,25,0.45)]" : ""
                  }`}
                >
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-[14px] border border-[#e5e7eb] bg-white text-[#fa5a19] dark:border-white/10 dark:bg-white/5">
                    <card.Icon className="h-5 w-5" />
                  </div>
                  <div className="mt-5 flex items-center justify-center gap-2">
                    <h3 className="text-lg font-semibold text-[#262626] dark:text-white">{card.title}</h3>
                    {card.badge ? (
                      <span className="rounded-full bg-[#fff0e8] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#fa5a19] dark:bg-[#fa5a19]/10">
                        {card.badge}
                      </span>
                    ) : null}
                  </div>
                  <p className="mt-3 text-sm leading-7 text-[#666666] dark:text-white/70">
                    {card.description}
                  </p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="career-card mx-auto max-w-[1216px] overflow-hidden rounded-[2rem]">
            <div className="grid border-b border-[#e5e7eb] px-6 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:px-10 dark:border-white/10">
              <div className="flex items-start">
                <p className="career-eyebrow text-xs font-semibold">Agent ready</p>
              </div>
              <div>
                <h2 className="career-display text-4xl font-semibold tracking-[-0.05em] text-[#262626] sm:text-5xl dark:text-white">
                  Easily connect with your
                  <span className="career-orange"> AI agents</span>
                </h2>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-[#666666] dark:text-white/70 sm:text-base">
                  Connect Aman Platform to finance-market agents, research workflows, and MCP-style tooling before scaling the same system to general web crawling.
                </p>
              </div>
            </div>
            <div className="grid gap-0 lg:grid-cols-2">
              {connectCards.map((card) => (
                <article key={card.title} className="border-t border-[#e5e7eb] p-6 lg:p-8 dark:border-white/10">
                  <h3 className="text-2xl font-semibold tracking-[-0.03em] text-[#262626] dark:text-white">
                    {card.title}
                  </h3>
                  <p className="mt-3 max-w-xl text-sm leading-7 text-[#666666] dark:text-white/70">
                    {card.description}
                  </p>
                  <div className="mt-6 rounded-[18px] border border-[#e5e7eb] bg-white/80 p-4 font-mono text-sm text-[#262626] dark:border-white/10 dark:bg-white/5 dark:text-white/80">
                    {card.code}
                  </div>
                  <a href="#developers" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[#fa5a19]">
                    {card.cta}
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            <SectionHeading
              eyebrow="Built for performance"
              title="Fast, reliable, and token-efficient. And it’s open source."
              text="Build the finance-and-research crawl layer first, then reuse that same reliable pipeline for broader agent workloads."
            />
            <div className="mt-10 grid gap-4 lg:grid-cols-2">
              {performanceCards.map((card) => (
                <article key={card.title} className="firecrawl-card rounded-[22px] p-6 lg:p-8">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-[14px] border border-[#e5e7eb] bg-white text-[#fa5a19] dark:border-white/10 dark:bg-white/5">
                      <card.Icon className="h-4.5 w-4.5" />
                    </div>
                    <p className="text-xs font-medium text-[#8b8b8b] dark:text-white/45">{card.eyebrow}</p>
                  </div>
                  <h3 className="mt-4 text-2xl font-semibold tracking-[-0.04em] text-[#262626] dark:text-white">
                    {card.title}
                  </h3>
                  <p className="mt-3 max-w-xl text-sm leading-7 text-[#666666] dark:text-white/70">
                    {card.text}
                  </p>
                  {card.cta ? (
                    <a href="#pricing" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[#fa5a19]">
                      {card.cta}
                      <ArrowRight className="h-4 w-4" />
                    </a>
                  ) : null}
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="career-card mx-auto grid max-w-[1216px] overflow-hidden rounded-[2rem] lg:grid-cols-[0.42fr_0.58fr]">
            <div className="border-b border-[#e5e7eb] p-6 lg:border-b-0 lg:border-r lg:p-8 dark:border-white/10">
              <p className="career-eyebrow text-xs font-semibold">Live web data</p>
              <h2 className="career-display mt-4 text-3xl font-semibold tracking-[-0.05em] text-[#262626] sm:text-5xl dark:text-white">
                Transform web data into
                <span className="career-orange"> AI-powered solutions</span>
              </h2>
              <p className="mt-4 text-sm leading-7 text-[#666666] dark:text-white/70">
                Start with finance research and high-signal crawl workflows, then expand the same system into broader chat, onboarding, and task-specific agent execution.
              </p>
              <div className="mt-8 space-y-3">
                {useCases.map((item, index) => (
                  <div
                    key={item.title}
                    className={`rounded-[18px] border px-4 py-4 ${
                      index === 0
                        ? "border-[#fa5a19]/25 bg-[#fff5f0] dark:border-[#fa5a19]/20 dark:bg-[#fa5a19]/5"
                        : "border-[#e5e7eb] bg-white/60 dark:border-white/10 dark:bg-white/5"
                    }`}
                  >
                    <p className={`text-base font-semibold ${index === 0 ? "text-[#fa5a19]" : "text-[#262626] dark:text-white"}`}>
                      {item.title}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-[#666666] dark:text-white/70">
                      {item.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
            <div className="p-6 lg:p-8">
              <div className="rounded-[24px] border border-[#e5e7eb] bg-white/80 p-5 dark:border-white/10 dark:bg-white/5">
                <div className="flex items-center gap-2 text-sm font-medium text-[#262626] dark:text-white">
                  <Search className="h-4 w-4 text-[#fa5a19]" />
                  Reliance Industries
                </div>
                <div className="mt-5 overflow-hidden rounded-[18px] border border-[#e5e7eb] dark:border-white/10">
                  {[
                    ["Exchange filings", "247 found"],
                    ["Market news", "1,832 found"],
                    ["Expert opinions", "89 found"],
                    ["Research reports", "156 found"],
                    ["Industry data", "423 found"],
                  ].map(([label, value]) => (
                    <div key={label} className="flex items-center justify-between border-b border-[#e5e7eb] px-4 py-3 last:border-b-0 dark:border-white/10">
                      <span className="text-sm text-[#666666] dark:text-white/65">{label}</span>
                      <span className="text-sm font-medium text-[#262626] dark:text-white">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="pricing" className="career-section-clean px-5 py-18 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            <SectionHeading
              eyebrow="Plans"
              title="Pricing that scales with your AI workspace"
              text="These plans are framed around what the current chat application already supports today and what the product can grow into next."
            />

            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              {pricingPlans.map((plan) => (
                <article
                  key={plan.name}
                  className={`rounded-[10px] border p-6 ${
                    plan.featured
                      ? "border-[#fa5a19]/30 bg-[#fff5f0] dark:border-[#fa5a19]/20 dark:bg-[#fa5a19]/5"
                      : "border-[#e5e7eb] bg-white dark:border-white/10 dark:bg-[#262626]"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-[15px] font-semibold text-[#262626] dark:text-white">{plan.name}</h3>
                    {plan.featured ? (
                      <span className="rounded-full border border-[#e5e7eb] bg-white/76 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#fa5a19] dark:border-white/10 dark:bg-[#262626] dark:text-[#fa5a19]">
                        Popular
                      </span>
                    ) : null}
                  </div>
                  <div className="mt-5 flex items-end gap-1">
                    <span className="text-4xl font-semibold tracking-[-0.05em]">
                      {plan.price}
                    </span>
                    {plan.period ? (
                      <span className="pb-1 text-sm text-slate-500 dark:text-slate-400">
                        {plan.period}
                      </span>
                    ) : null}
                  </div>
                  <p className="mt-3 text-sm leading-6 text-[#666666] dark:text-white/70">
                    {plan.description}
                  </p>
                  <ul className="mt-6 space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3 text-sm">
                        <span className="mt-1 h-2.5 w-2.5 rounded-full bg-[#fa5a19]" />
                        <span className="text-[#666666] dark:text-white/70">
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* ── FAQ ──────────────────────────────────────────────────────── */}
        <section className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-4xl">
            <SectionHeading
              eyebrow="FAQ"
              title="Frequently asked questions"
              text="These answers reflect the updated product direction: finance-and-research-first crawling, dedicated agents, and an open-source builder surface."
            />

            <div className="mt-10 space-y-3">
              {faqs.map((faq) => (
                <details
                  key={faq.question}
                  className="career-muted-card group rounded-[10px] px-5 py-4 dark:border-white/10 dark:bg-[#262626]">
                  <summary className="cursor-pointer list-none text-[13px] font-semibold text-[#262626] dark:text-white">
                    {faq.question}
                  </summary>
                  <p className="pt-3 text-sm leading-7 text-[#666666] dark:text-white/70">
                    {faq.answer}
                  </p>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA ──────────────────────────────────────────────────────── */}
        <section className="career-section px-5 py-18 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-[1216px]">
            <SectionHeading
              eyebrow="Community"
              title="People love building with AmanCrawl"
              text="Use social-proof style cards to reinforce that the product is useful for developers shipping finance, research, and later general crawl workflows."
            />
            <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {testimonials.map((item) => (
                <article key={item.name} className="firecrawl-card rounded-[22px] p-5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#fff1e8] text-[#fa5a19] dark:bg-[#fa5a19]/10">
                      <Users className="h-5 w-5" />
                    </div>
                    <p className="text-sm font-semibold text-[#262626] dark:text-white">{item.name}</p>
                  </div>
                  <p className="mt-4 text-sm leading-7 text-[#666666] dark:text-white/70">
                    “{item.quote}”
                  </p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="px-5 pt-8 pb-16 sm:px-8 lg:px-12">
          <div className="career-card-dark relative mx-auto max-w-[1216px] overflow-hidden rounded-[20px] px-6 py-14 text-white">
            <div className="career-sun absolute -right-20 -top-24 h-72 w-72 rounded-full opacity-70" />
            <div className="absolute inset-0 opacity-25">
              <FlickeringGrid
                squareSize={4}
                gridGap={10}
                color="rgb(250,90,25)"
                maxOpacity={0.15}
                className="h-full w-full"
              />
            </div>
            <div className="relative mx-auto max-w-3xl text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-white/60">
                Get started
              </p>
              <h2 className="career-display mt-5 text-balance text-4xl font-semibold tracking-[-0.05em] sm:text-6xl">
                Ready to build?
              </h2>
              <p className="mt-5 text-base leading-8 text-orange-50/90">
                Start building finance and research agents first, then expand into broader web crawling with the same grounded, open product surface.
              </p>
              <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
                <Link href="/signup" className="inline-block">
                  <button className="inline-flex h-10 items-center justify-center rounded-[8px] bg-white px-5 text-[13px] font-medium text-[#262626] transition hover:bg-[#f5f5f5] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40">
                    Start for free
                  </button>
                </Link>
                <Link
                  href="#pricing"
                  className="inline-flex items-center justify-center gap-2 rounded-[8px] border border-white/20 px-5 py-2.5 text-[13px] font-medium text-white transition hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40"
                >
                  See our plans
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
              <p className="mt-4 text-sm text-white/55">
                Are you an AI agent? Get an API key and start building.
              </p>
            </div>
          </div>
        </section>

        {/* ── Footer ───────────────────────────────────────────────────── */}
        <footer className="px-6 pb-14 sm:px-8 lg:px-12">
          <div className="mx-auto grid max-w-[1216px] gap-10 border-t border-[#e5e7eb] pt-8 text-sm text-[#666666] dark:border-white/10 dark:text-slate-400 lg:grid-cols-[1.2fr_0.8fr_0.8fr_0.8fr_0.8fr] lg:pl-1">
            <div>
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#fa5a19] text-white">
                  <Zap className="h-4 w-4" />
                </span>
                <span className="font-semibold text-[#262626] dark:text-white">
                  Aman Platform
                </span>
              </div>
              <p className="mt-4 max-w-xs leading-6">
                The open-source platform for AI Memory, Agents, and Web Intelligence. One platform, two products, one long-term AI operating system vision.
              </p>
              <div className="mt-5 grid grid-cols-2 gap-3 text-[#999999]">
                <div className="firecrawl-card rounded-[14px] px-3 py-2">
                  <span className="flex items-center gap-2"><Star className="h-4 w-4" /> Open source</span>
                </div>
                <div className="firecrawl-card rounded-[14px] px-3 py-2">
                  <span className="flex items-center gap-2"><ShieldCheck className="h-4 w-4" /> Secure</span>
                </div>
                <div className="firecrawl-card rounded-[14px] px-3 py-2">
                  <span className="flex items-center gap-2"><Code2 className="h-4 w-4" /> Developer-ready</span>
                </div>
                <div className="firecrawl-card rounded-[14px] px-3 py-2">
                  <span className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Grounded</span>
                </div>
              </div>
            </div>

            <FooterColumn
              title="Products"
              items={["AmanAgentLab", "AmanCrawl", "Pricing", "Changelog", "Self-hosting"]}
            />
            <FooterColumn
              title="Use Cases"
              items={["Memory & Context", "Web Intelligence", "AI Agents", "RAG Applications", "Deep Research"]}
            />
            <FooterColumn
              title="Documentation"
              items={["Getting started", "API Reference", "SDKs & Tools", "MCP Integration", "Self-hosting"]}
            />
            <FooterColumn
              title="Company"
              items={["About", "Blog", "Careers", "Community", "Open Source"]}
            />
          </div>
        </footer>
      </div>
    </main>
  );
}

function MegaMenuItem({
  item,
  isOpen,
  onOpen,
  onClose,
}: {
  item: typeof megaMenuItems[number];
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  const clearTimer = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const handleOpen = () => {
    clearTimer();
    onOpen();
  };

  const handleClose = () => {
    clearTimer();
    timeoutRef.current = setTimeout(() => onClose(), 150);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape" && isOpen) {
      onClose();
    }
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (isOpen) onClose();
      else onOpen();
    }
  };

  if (!("megaMenu" in item)) {
    return (
      <a href={item.href} className="transition hover:text-slate-950 dark:hover:text-white">
        {item.label}
      </a>
    );
  }

  return (
    <div
      className="relative z-50"
      onMouseEnter={handleOpen}
      onMouseLeave={handleClose}
    >
      <motion.button
        type="button"
        onMouseEnter={handleOpen}
        onClick={() => (isMobile ? (isOpen ? onClose() : onOpen()) : undefined)}
        onKeyDown={handleKeyDown}
        aria-expanded={isOpen}
        aria-haspopup="true"
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
        className={`flex cursor-pointer items-center gap-1 rounded-full px-2 py-1.5 transition-colors duration-150 ${
          isOpen
            ? "bg-[#fff2ea] text-slate-950 dark:bg-white/8 dark:text-white"
            : "hover:bg-[#fff2ea] hover:text-slate-950 dark:hover:bg-white/5 dark:hover:text-white"
        }`}
      >
        {item.label}
        <motion.span
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className="inline-flex h-3 w-3"
        >
          <ChevronDown className="h-3 w-3" />
        </motion.span>
      </motion.button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: -4, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            className="absolute left-1/2 top-full mt-3 w-[640px] -translate-x-1/2 z-50"
            onMouseEnter={handleOpen}
          >
            <div className="absolute inset-x-0 -top-3 h-3" />
            <div className="firecrawl-dropdown rounded-[24px] p-5">
              <div className="grid grid-cols-2 gap-x-8 gap-y-6">
                {item.megaMenu!.map((group) => (
                  <div key={group.title} className={group.items.length > 3 ? "col-span-2 grid grid-cols-2 gap-x-6" : ""}>
                    <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-[#a18672] dark:text-white/50">
                      {group.title}
                    </p>
                    <div className="space-y-1">
                      {group.items.map((sub) => (
                        <a
                          key={sub.label}
                          href={sub.href}
                          tabIndex={isOpen ? 0 : -1}
                          className="block rounded-[12px] px-3 py-2 transition hover:bg-[#fff2ea] dark:hover:bg-white/5"
                        >
                          <p className="text-xs font-medium text-[#201510] dark:text-white">
                            {sub.label}
                          </p>
                          <p className="mt-0.5 text-[11px] leading-snug text-[#666666] dark:text-white/50">
                            {sub.desc}
                          </p>
                        </a>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function SectionHeading({
  eyebrow,
  title,
  text,
  align = "center",
}: {
  eyebrow: string;
  title: string;
  text: string;
  align?: "center" | "left";
}) {
  const isLeft = align === "left";

  return (
    <div
      className={isLeft ? "max-w-2xl text-left" : "mx-auto max-w-3xl text-center"}
    >
      <p className="career-eyebrow text-xs font-semibold">{eyebrow}</p>
      <h2 className="career-display mt-4 text-balance text-3xl font-semibold tracking-[-0.05em] text-[#262626] sm:text-5xl dark:text-white">
        {title}
      </h2>
      <p className="mt-4 text-sm leading-7 text-[#666666] dark:text-white/70 sm:text-base">
        {text}
      </p>
    </div>
  );
}

function FooterColumn({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div>
      <p className="font-semibold text-[#262626] dark:text-white">{title}</p>
      <ul className="mt-4 space-y-2.5">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
