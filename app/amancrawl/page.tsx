"use client";
import Link from "next/link";
import { useState, useEffect, useRef, useCallback } from "react";
import {
  ArrowRight,
  Globe,
  Search,
  FileText,
  Code2,
  Shield,
  Zap,
  Database,
  GitBranch,
  X,
  Loader2,
  Sparkles,
  Copy,
  Check,
  Square,
  Brain,
  Eye,
  BarChart3,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  Cpu,
  Layers,
  Monitor,
  FileSearch,
  Globe2,
  Lock,
  Rocket,
  Map,
} from "lucide-react";

import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";
import SubscriptionModal from "@/components/SubscriptionModal";
import LimitReachedModal from "@/components/LimitReachedModal";
import UsageCounter from "@/components/UsageCounter";
import ResearchDemo from "@/components/amancrawl/ResearchDemo";
import PipelineVisualization from "@/components/amancrawl/PipelineVisualization";
import ScrollReveal from "@/components/motion/ScrollReveal";
import {
  scrapeUrl,
  crawlSite,
  mapSite,
  searchWeb,
  agentExtract,
  refinePrompt,
  intelligenceQuery,
  type ScrapeResult,
  type CrawlResult,
  type MapResult,
  type SearchResult,
  type AgentExtractResult,
  type IntelligenceStep,
  type IntelligencePlan,
  type IntelligenceResult,
  LimitReachedError,
} from "@/services/amancrawl";
import { buildAuthHeaders } from "@/lib/auth";
import type { AuthContext } from "@/lib/types";

/* ─── Feature Pillars ─── */
const FEATURE_PILLARS = [
  {
    icon: <Search className="w-6 h-6" />,
    title: "Knowledge Discovery",
    description: "Search, website mapping, discovery, and monitoring across the entire web.",
    features: ["Multi-provider Search", "Website Mapping", "Link Discovery", "Change Monitoring"],
    color: "#fa5a19",
  },
  {
    icon: <Database className="w-6 h-6" />,
    title: "Knowledge Extraction",
    description: "Scrape, crawl, extract structured data, screenshots, and metadata from any source.",
    features: ["Smart Scraping", "Deep Crawling", "Structured Data", "Screenshots & Metadata"],
    color: "#3ddc84",
  },
  {
    icon: <Brain className="w-6 h-6" />,
    title: "Knowledge Intelligence",
    description: "Research, entity extraction, relationship detection, knowledge graphs, and reports.",
    features: ["AI Research", "Entity Extraction", "Knowledge Graphs", "Intelligent Reports"],
    color: "#8b5cf6",
  },
  {
    icon: <Code2 className="w-6 h-6" />,
    title: "Agent Infrastructure",
    description: "API, SDK, MCP integration, browser automation, and agent workflow orchestration.",
    features: ["REST API & SDK", "MCP Integration", "Browser Automation", "Agent Workflows"],
    color: "#06b6d4",
  },
];

/* ─── Use Cases ─── */
const USE_CASES = [
  {
    icon: <BarChart3 className="w-5 h-5" />,
    title: "Deep Research",
    description: "Multi-source research reports with citations, entities, and structured analysis.",
    query: "Research the top 10 AI startups in 2026",
  },
  {
    icon: <Eye className="w-5 h-5" />,
    title: "Competitive Intelligence",
    description: "Monitor competitors, track pricing changes, and analyze market positioning.",
    query: "Track competitor pricing changes weekly",
  },
  {
    icon: <FileText className="w-5 h-5" />,
    title: "Documentation RAG",
    description: "Index entire documentation sites for retrieval-augmented generation systems.",
    query: "Crawl and index LangChain docs",
  },
  {
    icon: <Layers className="w-5 h-5" />,
    title: "Knowledge Graphs",
    description: "Build connected knowledge from the web with entity and relationship extraction.",
    query: "Map the AI agent ecosystem",
  },
  {
    icon: <Cpu className="w-5 h-5" />,
    title: "AI Agents",
    description: "Provide tools and context for autonomous agent research and decision-making.",
    query: "Give my agent web research capabilities",
  },
  {
    icon: <Monitor className="w-5 h-5" />,
    title: "Browser Automation",
    description: "Interact with dynamic websites, fill forms, and extract JavaScript-rendered content.",
    query: "Extract data from a SPA dashboard",
  },
];

/* ─── Social Proof ─── */
const BUILT_WITH = [
  "AI Research Agents",
  "RAG Platforms",
  "Market Intelligence",
  "Monitoring Systems",
  "Knowledge Graphs",
  "Browser Automation",
];

/* ─── Inline Result Views ─── */
function SearchResultsList({ data }: { data: SearchResult }) {
  return (
    <div className="space-y-3">
      {data.results?.map((r: any, i: number) => (
        <div key={i} className="p-4 bg-white/[0.03] border border-white/5 rounded-xl">
          <div className="flex items-center gap-2 mb-1">
            <Globe className="w-3.5 h-3.5 text-[#3ddc84]" />
            <span className="text-xs text-white/40">{r.url || r.link}</span>
          </div>
          <h4 className="text-white font-medium text-sm">{r.title}</h4>
          <p className="text-white/60 text-xs mt-1 line-clamp-2">{r.snippet || r.description}</p>
        </div>
      ))}
      {data.answer && (
        <div className="p-4 bg-[#fa5a19]/5 border border-[#fa5a19]/20 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-[#fa5a19]" />
            <span className="text-xs text-[#fa5a19] font-medium">AI Synthesis</span>
          </div>
          <p className="text-white/80 text-sm whitespace-pre-line">{data.answer}</p>
        </div>
      )}
    </div>
  );
}

function ScrapeResultView({ data }: { data: ScrapeResult }) {
  return (
    <div className="space-y-3">
      {data.title && (
        <div className="p-4 bg-white/[0.03] border border-white/5 rounded-xl">
          <h4 className="text-white font-medium text-sm">{data.title}</h4>
          <p className="text-white/40 text-xs mt-1">{data.url}</p>
        </div>
      )}
      {data.markdown && (
        <div className="p-4 bg-white/[0.03] border border-white/5 rounded-xl max-h-64 overflow-auto">
          <pre className="text-white/70 text-xs whitespace-pre-wrap font-mono">{data.markdown.slice(0, 3000)}</pre>
        </div>
      )}
      {data.answer && (
        <div className="p-4 bg-[#fa5a19]/5 border border-[#fa5a19]/20 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-[#fa5a19]" />
            <span className="text-xs text-[#fa5a19] font-medium">AI Analysis</span>
          </div>
          <p className="text-white/80 text-sm whitespace-pre-line">{data.answer}</p>
        </div>
      )}
    </div>
  );
}

function CrawlResultView({ data }: { data: CrawlResult }) {
  return (
    <div className="space-y-3">
      <div className="p-4 bg-white/[0.03] border border-white/5 rounded-xl">
        <div className="flex items-center justify-between">
          <span className="text-white/60 text-sm">Pages crawled</span>
          <span className="text-[#3ddc84] font-bold text-lg">{data.pages_crawled || 0}</span>
        </div>
      </div>
      {data.pages?.slice(0, 5).map((p: any, i: number) => (
        <div key={i} className="p-3 bg-white/[0.02] border border-white/5 rounded-lg">
          <div className="text-white/80 text-xs font-medium">{p.url}</div>
          <div className="text-white/40 text-xs mt-1 line-clamp-2">{p.content?.slice(0, 150)}</div>
        </div>
      ))}
      {data.answer && (
        <div className="p-4 bg-[#fa5a19]/5 border border-[#fa5a19]/20 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-[#fa5a19]" />
            <span className="text-xs text-[#fa5a19] font-medium">AI Synthesis</span>
          </div>
          <p className="text-white/80 text-sm whitespace-pre-line">{data.answer}</p>
        </div>
      )}
    </div>
  );
}

function MapResultView({ data }: { data: MapResult }) {
  return (
    <div className="space-y-3">
      <div className="p-4 bg-white/[0.03] border border-white/5 rounded-xl">
        <div className="flex items-center justify-between">
          <span className="text-white/60 text-sm">Links discovered</span>
          <span className="text-[#8b5cf6] font-bold text-lg">{data.links?.length || 0}</span>
        </div>
      </div>
      <div className="p-4 bg-white/[0.03] border border-white/5 rounded-xl max-h-64 overflow-auto">
        {data.links?.slice(0, 30).map((link: string, i: number) => (
          <div key={i} className="flex items-center gap-2 py-1.5 border-b border-white/5 last:border-0">
            <ExternalLink className="w-3 h-3 text-white/30 shrink-0" />
            <span className="text-white/60 text-xs truncate">{link}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AgentResultView({ data }: { data: AgentExtractResult }) {
  return (
    <div className="space-y-3">
      {data.result != null && (
        <div className="p-4 bg-[#fa5a19]/5 border border-[#fa5a19]/20 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-[#fa5a19]" />
            <span className="text-xs text-[#fa5a19] font-medium">Extracted Data</span>
          </div>
          <pre className="text-white/80 text-xs whitespace-pre-wrap font-mono">{String(data.result)}</pre>
        </div>
      )}
      {data.raw_content && (
        <div className="p-4 bg-white/[0.03] border border-white/5 rounded-xl max-h-48 overflow-auto">
          <pre className="text-white/60 text-xs whitespace-pre-wrap font-mono">{data.raw_content.slice(0, 2000)}</pre>
        </div>
      )}
    </div>
  );
}

/* ─── Main Page ─── */
export default function AmanCrawlPage() {
  const [activeTab, setActiveTab] = useState<"search" | "scrape" | "agent" | "map" | "crawl" | "intelligence">("search");
  const [url, setUrl] = useState("");
  const [instruction, setInstruction] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [user, setUser] = useState<AuthContext | null>(null);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [showLimitModal, setShowLimitModal] = useState(false);
  const [limitError, setLimitError] = useState<LimitReachedError | null>(null);
  const [usageRefresh, setUsageRefresh] = useState(0);
  const [copied, setCopied] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [intelSteps, setIntelSteps] = useState<IntelligenceStep[]>([]);
  const [intelPlan, setIntelPlan] = useState<IntelligencePlan | null>(null);
  const [intelResult, setIntelResult] = useState<IntelligenceResult | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const ctx = (window as any).__authContext;
    if (ctx) setUser(ctx);
  }, []);

  const tabs = [
    { key: "search" as const, label: "Search", icon: <Search className="w-4 h-4" /> },
    { key: "scrape" as const, label: "Scrape", icon: <Globe className="w-4 h-4" /> },
    { key: "agent" as const, label: "Agent", icon: <Sparkles className="w-4 h-4" /> },
    { key: "map" as const, label: "Map", icon: <Map className="w-4 h-4" /> },
    { key: "crawl" as const, label: "Crawl", icon: <FileText className="w-4 h-4" /> },
    { key: "intelligence" as const, label: "Intelligence", icon: <Brain className="w-4 h-4" /> },
  ];

  const handleSubmit = useCallback(async () => {
    if (!url.trim() && activeTab !== "search" && activeTab !== "intelligence") return;
    if (!url.trim() && activeTab === "search") return;

    setLoading(true);
    setError(null);
    setResult(null);
    setIntelSteps([]);
    setIntelPlan(null);
    setIntelResult(null);
    abortRef.current = new AbortController();

    try {
      if (activeTab === "intelligence") {
        await intelligenceQuery(
          url,
          {
            onStep: (step) => {
              setIntelSteps((prev) => {
                const idx = prev.findIndex((s) => s.step === step.step);
                if (idx >= 0) {
                  const next = [...prev];
                  next[idx] = step;
                  return next;
                }
                return [...prev, step];
              });
            },
            onPlan: (plan) => {
              setIntelPlan(plan);
            },
            onResult: (result) => {
              setIntelResult(result);
            },
            onError: (message, issues) => {
              setError(message);
              if (issues?.length) {
                setError(`${message}: ${issues.join(", ")}`);
              }
            },
            onDone: () => {
              setLoading(false);
            },
          },
          abortRef.current.signal,
        );
        return;
      }

      let res: any;
      if (activeTab === "scrape") {
        res = await scrapeUrl(url, ["markdown"], instruction, abortRef.current.signal);
      } else if (activeTab === "agent") {
        res = await agentExtract(url, instruction || "Extract all key information", undefined, undefined, abortRef.current.signal);
      } else if (activeTab === "crawl") {
        if (!user || user.scopes?.includes("crawl:scrape")) {
          res = await crawlSite(url, 20, instruction, abortRef.current.signal);
        } else {
          setShowSubscriptionModal(true);
          setLoading(false);
          return;
        }
      } else if (activeTab === "map") {
        res = await mapSite(url, instruction, abortRef.current.signal);
      } else if (activeTab === "search") {
        res = await searchWeb(url, 10, instruction, abortRef.current.signal);
      }
      setResult(res);
      setUsageRefresh((p) => p + 1);
    } catch (e: any) {
      if (e?.name === "AbortError") return;
      if (e instanceof LimitReachedError) {
        setLimitError(e);
        setShowLimitModal(true);
      } else {
        setError(e?.message || "Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  }, [url, instruction, activeTab, user]);

  const handleStop = () => {
    abortRef.current?.abort();
    setLoading(false);
  };

  const copyResult = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* ─── Header ─── */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#fa5a19] to-[#ff8c42] flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-semibold text-lg">AmanCrawl</span>
          </Link>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-white/50 hover:text-white text-sm transition-colors">Features</a>
            <a href="#pipeline" className="text-white/50 hover:text-white text-sm transition-colors">Pipeline</a>
            <a href="#use-cases" className="text-white/50 hover:text-white text-sm transition-colors">Use Cases</a>
            <a href="#developer" className="text-white/50 hover:text-white text-sm transition-colors">Developer</a>
          </nav>
          <div className="flex items-center gap-3">
            <AnimatedThemeToggler />
            {user ? (
              <Link
                href="/chat"
                className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-all"
              >
                Dashboard
              </Link>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 bg-[#fa5a19] rounded-lg text-sm text-white font-medium hover:bg-[#ff6b2b] transition-all"
              >
                Get Started
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* ─── Hero Section ─── */}
      <section className="pt-28 pb-24 px-6 relative overflow-hidden min-h-[90vh] flex items-center">
        {/* Background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[700px] bg-[#fa5a19]/3 rounded-full blur-[150px] pointer-events-none" />

        {/* Decorative corner labels */}
        <div className="absolute top-32 left-8 text-white/10 text-xs font-mono hidden lg:block">{"[ 200 OK ]"}</div>
        <div className="absolute top-32 right-8 text-white/10 text-xs font-mono hidden lg:block">{"[ SCRAPE ]"}</div>
        <div className="absolute bottom-40 left-8 text-white/10 text-xs font-mono hidden lg:block">{"[ .JSON ]"}</div>
        <div className="absolute bottom-40 right-8 text-white/10 text-xs font-mono hidden lg:block">{"[ .MD ]"}</div>

        {/* Decorative dots */}
        <div className="absolute top-40 left-1/4 w-2 h-2 rounded-full bg-[#fa5a19]/30" />
        <div className="absolute top-52 right-1/3 w-1.5 h-1.5 rounded-full bg-[#fa5a19]/20" />
        <div className="absolute bottom-48 left-1/3 w-1 h-1 rounded-full bg-[#3ddc84]/20" />
        <div className="absolute top-60 left-1/2 w-1 h-1 rounded-full bg-[#8b5cf6]/20" />

        <div className="max-w-4xl mx-auto text-center relative z-10 w-full">
          {/* Announcement banner */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#fa5a19]/10 border border-[#fa5a19]/20 rounded-full text-sm text-[#fa5a19] mb-10 cursor-pointer hover:bg-[#fa5a19]/15 transition-all">
            <Zap className="w-3.5 h-3.5" />
            <span>Introducing Knowledge Intelligence — AI-powered research with SOTA recall.</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>

          {/* Headline — Firecrawl style */}
          <h1 className="text-5xl md:text-7xl lg:text-[82px] font-bold tracking-tight mb-6 leading-[1.05]">
            <span className="text-white">Power AI agents with</span>
            <br />
            <span className="bg-gradient-to-r from-[#fa5a19] to-[#ff8c42] bg-clip-text text-transparent">
              clean web data
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-white/50 text-lg md:text-xl max-w-xl mx-auto mb-12 leading-relaxed">
            The API to search, scrape, and interact
            <br className="hidden md:block" />
            with the web at scale.{" "}
            <span className="text-white/70">It&apos;s also open source.</span>
          </p>

          {/* Search Card — Firecrawl style */}
          <div className="max-w-2xl mx-auto mb-6">
            <div className="relative bg-[#111111] border border-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-black/50 p-1">
              {/* Input row */}
              <div className="flex items-center gap-3 px-5 py-4">
                <Globe className="w-5 h-5 text-white/30 shrink-0" />
                <input
                  ref={inputRef}
                  type="text"
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value);
                    if (e.target.value.match(/^https?:\/\//)) {
                      setActiveTab("scrape");
                    }
                  }}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                  placeholder={activeTab === "search" || activeTab === "intelligence" ? "Ask anything..." : "https://example.com"}
                  className="flex-1 bg-transparent text-white text-lg placeholder:text-white/25 outline-none font-light"
                />
                {loading ? (
                  <button
                    onClick={handleStop}
                    className="w-11 h-11 rounded-xl bg-red-500/20 border border-red-500/30 flex items-center justify-center hover:bg-red-500/30 transition-all shrink-0"
                  >
                    <Square className="w-4 h-4 text-red-400" />
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    className="w-11 h-11 rounded-xl bg-[#fa5a19] flex items-center justify-center hover:bg-[#ff6b2b] transition-all shrink-0"
                  >
                    <ArrowRight className="w-5 h-5 text-white" />
                  </button>
                )}
              </div>

              {/* Tabs row — inside the card */}
              <div className="flex items-center gap-1 px-4 pb-3 pt-1 border-t border-white/5">
                {tabs.map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                      activeTab === tab.key
                        ? "bg-white/10 text-white"
                        : "text-white/40 hover:text-white/60 hover:bg-white/5"
                    }`}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Setup for agents link */}
          <div className="flex items-center justify-center gap-2 text-sm text-white/40 hover:text-white/60 transition-colors cursor-pointer mb-4">
            <Code2 className="w-4 h-4" />
            <span>Setup for agents</span>
          </div>

          {/* Example Queries */}
          <div className="flex flex-wrap gap-2 justify-center mt-8">
            {[
              "Research AI browser startups",
              "Compare LangGraph vs CrewAI",
              "Extract pricing from SaaS websites",
              "Monitor competitor changes",
              "Crawl documentation sites",
            ].map((q, i) => (
              <button
                key={i}
                onClick={() => {
                  setUrl(q);
                  setActiveTab("search");
                  inputRef.current?.focus();
                }}
                className="px-3.5 py-1.5 bg-white/[0.04] border border-white/5 rounded-lg text-xs text-white/40 hover:text-white/60 hover:bg-white/[0.08] transition-all hover-lift"
                style={{ animation: `stagger-child 0.5s var(--ease-spring) ${400 + i * 60}ms both` }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Live Execution Result ─── */}
      {(loading || result || error || intelSteps.length > 0 || intelResult) && (
        <section className="pb-20 px-6">
          <div className="max-w-3xl mx-auto">
            {loading && activeTab !== "intelligence" && (
              <div className="bg-[#111111] border border-white/5 rounded-2xl p-8">
                <div className="flex items-center gap-3 mb-6">
                  <Loader2 className="w-5 h-5 text-[#fa5a19] animate-spin" />
                  <span className="text-white font-medium">Researching...</span>
                </div>
                <div className="space-y-3">
                  {["Searching web", "Discovering sources", "Crawling pages", "Extracting entities", "Building knowledge", "Generating report"].map(
                    (step, i) => (
                      <div key={i} className="flex items-center gap-3 text-white/40">
                        <CheckCircle2 className={`w-4 h-4 ${i < 2 ? "text-[#3ddc84]" : "text-white/20"}`} />
                        <span className="text-sm">{step}</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {activeTab === "intelligence" && intelSteps.length > 0 && (
              <div className="bg-[#111111] border border-white/5 rounded-2xl p-8 mb-4">
                <div className="flex items-center gap-3 mb-6">
                  <Loader2 className="w-5 h-5 text-[#fa5a19] animate-spin" />
                  <span className="text-white font-medium">Intelligence Pipeline</span>
                </div>
                <div className="space-y-3">
                  {intelSteps.map((step, i) => (
                    <div key={i} className="flex items-center gap-3">
                      {step.status === "complete" ? (
                        <CheckCircle2 className="w-4 h-4 text-[#3ddc84] shrink-0" />
                      ) : step.status === "error" ? (
                        <X className="w-4 h-4 text-red-400 shrink-0" />
                      ) : (
                        <Loader2 className="w-4 h-4 text-[#fa5a19] animate-spin shrink-0" />
                      )}
                      <span className={`text-sm ${step.status === "complete" ? "text-white/60" : step.status === "error" ? "text-red-400" : "text-white"}`}>
                        {step.step === "security" && "Security validation"}
                        {step.step === "planner" && "Planning execution"}
                        {step.step === "router" && "Routing to agents"}
                        {step.step === "knowledge_store" && "Storing knowledge"}
                        {!["security", "planner", "router", "knowledge_store"].includes(step.step) && step.step}
                      </span>
                      {step.elapsed_ms != null && (
                        <span className="text-xs text-white/30 ml-auto">{Math.round(step.elapsed_ms)}ms</span>
                      )}
                    </div>
                  ))}
                </div>

                {intelPlan && (
                  <div className="mt-6 p-4 bg-white/[0.03] border border-white/5 rounded-xl">
                    <div className="flex items-center gap-2 mb-3">
                      <Brain className="w-4 h-4 text-[#8b5cf6]" />
                      <span className="text-xs text-[#8b5cf6] font-medium uppercase tracking-wider">Plan</span>
                      <span className="ml-auto text-xs text-white/40">{intelPlan.query_type} · {intelPlan.confidence.toFixed(0)}% confidence</span>
                    </div>
                    <div className="space-y-2">
                      {intelPlan.steps.map((s, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                          <span className="w-5 h-5 rounded bg-white/5 flex items-center justify-center text-xs text-white/40">{i + 1}</span>
                          <span className="text-white/70">{s.description}</span>
                          <span className="ml-auto text-xs text-white/30 font-mono">{s.agent}</span>
                        </div>
                      ))}
                    </div>
                    <p className="mt-3 text-xs text-white/40 italic">{intelPlan.reasoning}</p>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-6">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {intelResult && !loading && (
              <div className="relative">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(intelResult, null, 2));
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="absolute top-4 right-4 z-10 p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all"
                >
                  {copied ? <Check className="w-4 h-4 text-[#3ddc84]" /> : <Copy className="w-4 h-4 text-white/40" />}
                </button>

                {intelResult.answer && (
                  <div className="p-6 bg-[#111111] border border-white/5 rounded-2xl mb-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Sparkles className="w-4 h-4 text-[#fa5a19]" />
                      <span className="text-xs text-[#fa5a19] font-medium uppercase tracking-wider">Answer</span>
                      <span className="ml-auto text-xs text-white/30">{intelResult.agents_used.join(", ")}</span>
                    </div>
                    <p className="text-white/80 text-sm whitespace-pre-line leading-relaxed">{intelResult.answer}</p>
                  </div>
                )}

                {intelResult.sources.length > 0 && (
                  <div className="p-5 bg-white/[0.03] border border-white/5 rounded-2xl mb-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Globe className="w-4 h-4 text-[#3ddc84]" />
                      <span className="text-xs text-[#3ddc84] font-medium uppercase tracking-wider">Sources ({intelResult.sources.length})</span>
                    </div>
                    <div className="space-y-2">
                      {intelResult.sources.map((s, i) => (
                        <div key={i} className="p-3 bg-white/[0.02] border border-white/5 rounded-lg">
                          {s.title && <p className="text-white/80 text-sm font-medium">{s.title}</p>}
                          {s.url && <p className="text-[#3ddc84] text-xs truncate">{s.url}</p>}
                          {s.snippet && <p className="text-white/50 text-xs mt-1 line-clamp-2">{s.snippet}</p>}
                          {s.summary && <p className="text-white/60 text-xs mt-1">{s.summary}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {intelResult.entities.length > 0 && (
                  <div className="p-5 bg-white/[0.03] border border-white/5 rounded-2xl mb-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Database className="w-4 h-4 text-[#8b5cf6]" />
                      <span className="text-xs text-[#8b5cf6] font-medium uppercase tracking-wider">Entities ({intelResult.entities.length})</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {intelResult.entities.map((e, i) => (
                        <span key={i} className="px-3 py-1.5 bg-[#8b5cf6]/10 border border-[#8b5cf6]/20 rounded-lg text-xs text-[#8b5cf6]/80">
                          <span className="font-medium">{e.name}</span>
                          <span className="text-white/30 ml-1.5">{e.type}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {intelResult.relationships.length > 0 && (
                  <div className="p-5 bg-white/[0.03] border border-white/5 rounded-2xl mb-4">
                    <div className="flex items-center gap-2 mb-3">
                      <GitBranch className="w-4 h-4 text-[#06b6d4]" />
                      <span className="text-xs text-[#06b6d4] font-medium uppercase tracking-wider">Relationships ({intelResult.relationships.length})</span>
                    </div>
                    <div className="space-y-1.5">
                      {intelResult.relationships.map((r, i) => (
                        <div key={i} className="text-xs text-white/50">
                          <span className="text-white/70">{r.source}</span>
                          <span className="mx-1.5 text-[#06b6d4]">→ {r.type} →</span>
                          <span className="text-white/70">{r.target}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between p-4 bg-white/[0.02] border border-white/5 rounded-xl">
                  <div className="flex items-center gap-4 text-xs text-white/30">
                    <span>{intelResult.execution_time_ms.toFixed(0)}ms</span>
                    <span>{intelResult.agents_used.length} agents</span>
                    <span>{intelResult.plan.steps} steps</span>
                  </div>
                  <span className="text-xs text-white/20 font-mono">{intelResult.query_type}</span>
                </div>
              </div>
            )}

            {result && !loading && activeTab !== "intelligence" && (
              <div className="relative">
                <button
                  onClick={copyResult}
                  className="absolute top-4 right-4 z-10 p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all"
                >
                  {copied ? <Check className="w-4 h-4 text-[#3ddc84]" /> : <Copy className="w-4 h-4 text-white/40" />}
                </button>
                {activeTab === "search" && <SearchResultsList data={result} />}
                {activeTab === "scrape" && <ScrapeResultView data={result} />}
                {activeTab === "crawl" && <CrawlResultView data={result} />}
                {activeTab === "map" && <MapResultView data={result} />}
                {activeTab === "agent" && <AgentResultView data={result} />}
              </div>
            )}
          </div>
        </section>
      )}

      {/* ─── Usage Counter ─── */}
      {user && (
        <section className="pb-16 px-6">
          <div className="max-w-4xl mx-auto">
            <UsageCounter horizontal refreshTrigger={usageRefresh} />
          </div>
        </section>
      )}

      {/* ─── Feature Pillars ─── */}
      <section id="features" className="py-24 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                The Complete Web Intelligence Stack
              </h2>
              <p className="text-white/50 text-lg max-w-2xl mx-auto">
                Four pillars that transform how AI systems discover, extract, and reason over web information.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {FEATURE_PILLARS.map((pillar, i) => (
              <ScrollReveal key={i} delay={i * 100}>
                <div
                  className="group p-8 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.04] hover:border-white/10 transition-all duration-500 hover-lift"
                >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-5"
                  style={{ backgroundColor: `${pillar.color}15`, color: pillar.color }}
                >
                  {pillar.icon}
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{pillar.title}</h3>
                <p className="text-white/50 text-sm leading-relaxed mb-5">{pillar.description}</p>
                <div className="flex flex-wrap gap-2">
                   {pillar.features.map((f, j) => (
                    <span
                      key={j}
                      className="px-3 py-1 bg-white/5 border border-white/5 rounded-lg text-xs text-white/50"
                    >
                      {f}
                    </span>
                  ))}
                </div>
              </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Interactive Research Demo ─── */}
      <section className="py-24 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Research, Don&apos;t Just Scrape
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              See how AmanCrawl transforms queries into structured knowledge with sources, entities, and reports.
            </p>
          </div>
          <ResearchDemo />
        </div>
      </section>

      {/* ─── Pipeline Visualization ─── */}
      <section id="pipeline" className="py-24 px-6 border-t border-white/5 bg-[#050505]">
        <PipelineVisualization />
      </section>

      {/* ─── Use Cases ─── */}
      <section id="use-cases" className="py-24 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                What You Can Build
              </h2>
              <p className="text-white/50 text-lg max-w-2xl mx-auto">
                From deep research to real-time monitoring, AmanCrawl powers the next generation of AI applications.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {USE_CASES.map((uc, i) => (
              <ScrollReveal key={i} delay={i * 80}>
                <div
                  className="group p-6 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.04] hover:border-white/10 transition-all duration-300 cursor-pointer hover-lift"
                >
                <div className="w-10 h-10 rounded-xl bg-[#fa5a19]/10 flex items-center justify-center text-[#fa5a19] mb-4">
                  {uc.icon}
                </div>
                <h3 className="text-white font-semibold mb-2">{uc.title}</h3>
                <p className="text-white/50 text-sm leading-relaxed mb-4">{uc.description}</p>
                <div className="flex items-center gap-2 text-xs text-white/30 group-hover:text-[#fa5a19]/60 transition-colors">
                  <span className="font-mono">&quot;{uc.query}&quot;</span>
                  <ChevronRight className="w-3 h-3" />
                </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Developer Section ─── */}
      <section id="developer" className="py-24 px-6 border-t border-white/5 bg-[#050505]">
        <div className="max-w-5xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                Built for Developers
              </h2>
              <p className="text-white/50 text-lg max-w-2xl mx-auto">
                Simple APIs that return structured intelligence, not raw HTML.
              </p>
            </div>
          </ScrollReveal>

          {/* Code Example */}
          <ScrollReveal delay={100}>
          <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden">
            <div className="flex items-center gap-2 px-5 py-3 border-b border-white/5">
              <div className="w-3 h-3 rounded-full bg-red-500/50" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
              <div className="w-3 h-3 rounded-full bg-green-500/50" />
              <span className="text-white/30 text-xs ml-2 font-mono">intelligence.ts</span>
            </div>
            <div className="p-6 overflow-x-auto">
              <pre className="text-sm font-mono leading-relaxed">
                <span className="text-[#8b5cf6]">const</span>{" "}
                <span className="text-white">result</span>{" "}
                <span className="text-white/40">=</span>{" "}
                <span className="text-[#8b5cf6]">await</span>{" "}
                <span className="text-[#3ddc84]">amanCrawl</span>
                <span className="text-white/40">.</span>
                <span className="text-[#fa5a19]">research</span>
                <span className="text-white/40">({"{"}</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">query</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-[#3ddc84]">&quot;Top browser AI startups&quot;</span>
                <span className="text-white/40">,</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">depth</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-[#3ddc84]">&quot;deep&quot;</span>
                <span className="text-white/40">,</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">extract</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-white/40">[</span>
                <span className="text-[#3ddc84]">&quot;company&quot;</span>
                <span className="text-white/40">,</span>{" "}
                <span className="text-[#3ddc84]">&quot;pricing&quot;</span>
                <span className="text-white/40">,</span>{" "}
                <span className="text-[#3ddc84]">&quot;features&quot;</span>
                <span className="text-white/40">]</span>
                {"\n"}
                <span className="text-white/40">{"});"}</span>
                {"\n\n"}
                <span className="text-white/30">{"// Result:"}</span>
                {"\n"}
                <span className="text-white/40">{"{"}</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">companies</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-white/40">[{"{...}"},</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">analysis</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-[#3ddc84]">&quot;...&quot;</span>
                <span className="text-white/40">,</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">sources</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-white/40">[{"{...}"}],</span>
                {"\n"}
                {"  "}
                <span className="text-[#06b6d4]">confidence</span>
                <span className="text-white/40">:</span>{" "}
                <span className="text-[#fa5a19]">0.94</span>
                {"\n"}
                <span className="text-white/40">{"}"}</span>
              </pre>
            </div>
          </div>
          </ScrollReveal>

          {/* API Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            {[
              { icon: <Rocket className="w-5 h-5" />, title: "REST API", desc: "Simple HTTP endpoints for every intelligence operation" },
              { icon: <Code2 className="w-5 h-5" />, title: "TypeScript SDK", desc: "First-class SDK with full type safety and streaming support" },
              { icon: <Lock className="w-5 h-5" />, title: "MCP Integration", desc: "Connect directly to AI agents via Model Context Protocol" },
            ].map((item, i) => (
              <ScrollReveal key={i} delay={200 + i * 100}>
                <div className="p-6 bg-white/[0.02] border border-white/5 rounded-2xl text-center hover-lift">
                <div className="w-10 h-10 rounded-xl bg-[#fa5a19]/10 flex items-center justify-center text-[#fa5a19] mx-auto mb-4">
                  {item.icon}
                </div>
                <h4 className="text-white font-semibold mb-2">{item.title}</h4>
                <p className="text-white/50 text-sm">{item.desc}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Social Proof ─── */}
      <section className="py-24 px-6 border-t border-white/5">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-white/30 text-sm uppercase tracking-widest mb-8">What developers are building</p>
          <div className="flex flex-wrap justify-center gap-4">
            {BUILT_WITH.map((item, i) => (
              <div
                key={i}
                className="px-5 py-3 bg-white/[0.03] border border-white/5 rounded-xl text-white/60 text-sm font-medium hover:bg-white/[0.06] hover:text-white/80 transition-all"
              >
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section className="py-24 px-6 border-t border-white/5">
        <ScrollReveal direction="scale">
          <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Start Building Intelligence
          </h2>
          <p className="text-white/50 text-lg mb-10 max-w-xl mx-auto">
            Transform how your AI systems discover, extract, and reason over web information.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="px-8 py-4 bg-[#fa5a19] rounded-xl text-white font-semibold hover:bg-[#ff6b2b] transition-all shadow-lg shadow-[#fa5a19]/25"
            >
              Get Started Free
            </Link>
            <a
              href="#developer"
              className="px-8 py-4 bg-white/5 border border-white/10 rounded-xl text-white/70 font-semibold hover:bg-white/10 hover:text-white transition-all"
            >
              View Documentation
            </a>
          </div>
        </div>
        </ScrollReveal>
      </section>

      {/* ─── Footer ─── */}
      <footer className="py-12 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-[#fa5a19] to-[#ff8c42] flex items-center justify-center">
              <Zap className="w-3 h-3 text-white" />
            </div>
            <span className="text-white/40 text-sm">AmanCrawl — Web Intelligence Platform</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/" className="text-white/40 hover:text-white/60 text-sm transition-colors">Home</Link>
            <Link href="/login" className="text-white/40 hover:text-white/60 text-sm transition-colors">Login</Link>
            <Link href="/signup" className="text-white/40 hover:text-white/60 text-sm transition-colors">Sign Up</Link>
          </div>
        </div>
      </footer>

      {/* Modals */}
      {showSubscriptionModal && (
        <SubscriptionModal isOpen={showSubscriptionModal} onClose={() => setShowSubscriptionModal(false)} feature="general" />
      )}
    </div>
  );
}
