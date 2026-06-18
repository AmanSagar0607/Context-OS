"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Globe, FileText, Database, CheckCircle2, Loader2, ExternalLink, Sparkles } from "lucide-react";

const DEMO_QUERIES = [
  {
    query: "Compare OpenAI and Anthropic",
    sources: 24,
    entities: [
      { type: "Company", name: "OpenAI", detail: "Creator of GPT-4, ChatGPT, DALL-E" },
      { type: "Company", name: "Anthropic", detail: "Creator of Claude, Constitutional AI" },
      { type: "Product", name: "GPT-4o", detail: "OpenAI's flagship multimodal model" },
      { type: "Product", name: "Claude 3.5", detail: "Anthropic's latest reasoning model" },
    ],
    report: `OpenAI and Anthropic are the two leading AI safety-focused companies. OpenAI, founded in 2015, pioneered large-scale language models with GPT series. Anthropic, founded in 2021 by former OpenAI members, focuses on AI safety through Constitutional AI.\n\nKey differences:\n- **Architecture**: OpenAI uses transformer-based models; Anthropic uses RLHF + Constitutional AI\n- **Safety**: Anthropic prioritizes safety research; OpenAI balances safety with capability\n- **Pricing**: Both offer tiered APIs; Claude is competitive with GPT-4 pricing\n- **Ecosystem**: OpenAI has broader plugin ecosystem; Anthropic focuses on enterprise`,
  },
  {
    query: "Research AI browser automation startups",
    sources: 18,
    entities: [
      { type: "Company", name: "Browserbase", detail: "Cloud browser infrastructure for AI agents" },
      { type: "Company", name: "Playwright", detail: "Microsoft's browser automation framework" },
      { type: "Company", name: "Stagehand", detail: "AI-native browser automation" },
      { type: "Technology", name: "Puppeteer", detail: "Chrome DevTools Protocol library" },
    ],
    report: `The browser automation space is rapidly evolving for AI agents. Key players include Browserbase (cloud infrastructure), Playwright (Microsoft's framework), and Stagehand (AI-native approach).\n\nMarket trends:\n- Shift from scripted automation to AI-driven interaction\n- Cloud browser sessions for scalable agent deployment\n- Vision-based page understanding replacing DOM parsing\n- Anti-bot detection and fingerprint management`,
  },
  {
    query: "Extract pricing from top 5 vector databases",
    sources: 12,
    entities: [
      { type: "Product", name: "Pinecone", detail: "Serverless vector database" },
      { type: "Product", name: "Weaviate", detail: "Open-source vector search engine" },
      { type: "Product", name: "Qdrant", detail: "High-performance vector similarity search" },
      { type: "Product", name: "Milvus", detail: "Scalable vector database for AI" },
      { type: "Product", name: "Chroma", detail: "Open-source embedding database" },
    ],
    report: `Vector database pricing varies significantly across providers:\n\n- **Pinecone**: Free tier (100K vectors), Starter ($0.33/hr), Enterprise (custom)\n- **Weaviate**: Free (14-day trial), Cloud from $25/mo, Self-hosted (free)\n- **Qdrant**: Free tier (1GB), Cloud from $0.035/hr, Enterprise (custom)\n- **Milvus**: Open-source (free), Zilliz Cloud from $0.058/hr\n- **Chroma**: Open-source (free), Cloud beta (pricing TBD)\n\nBest value for startups: Chroma (open-source) or Qdrant (generous free tier).`,
  },
];

type Step = {
  label: string;
  icon: React.ReactNode;
  status: "pending" | "active" | "done";
};

export default function ResearchDemo() {
  const [selectedQuery, setSelectedQuery] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [showResults, setShowResults] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const stepTimerRef = useRef<NodeJS.Timeout | null>(null);

  const demo = DEMO_QUERIES[selectedQuery];

  const steps: Step[] = [
    { label: "Searching web", icon: <Search className="w-3.5 h-3.5" />, status: "pending" },
    { label: "Discovering sources", icon: <Globe className="w-3.5 h-3.5" />, status: "pending" },
    { label: "Crawling pages", icon: <FileText className="w-3.5 h-3.5" />, status: "pending" },
    { label: "Extracting entities", icon: <Database className="w-3.5 h-3.5" />, status: "pending" },
    { label: "Building knowledge", icon: <Sparkles className="w-3.5 h-3.5" />, status: "pending" },
    { label: "Generating report", icon: <CheckCircle2 className="w-3.5 h-3.5" />, status: "pending" },
  ];

  const runDemo = (queryIndex: number) => {
    setSelectedQuery(queryIndex);
    setIsRunning(true);
    setShowResults(false);
    setCurrentStep(0);
    setInputValue(DEMO_QUERIES[queryIndex].query);
  };

  useEffect(() => {
    if (!isRunning || currentStep < 0) return;

    if (currentStep >= steps.length) {
      setIsRunning(false);
      setShowResults(true);
      return;
    }

    stepTimerRef.current = setTimeout(() => {
      setCurrentStep((prev) => prev + 1);
    }, 600 + Math.random() * 400);

    return () => {
      if (stepTimerRef.current) clearTimeout(stepTimerRef.current);
    };
  }, [currentStep, isRunning]);

  const getStepStatus = (index: number): "pending" | "active" | "done" => {
    if (index < currentStep) return "done";
    if (index === currentStep && isRunning) return "active";
    return "pending";
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Query Input */}
      <div className="relative mb-6">
        <div className="relative bg-[#1a1a1a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
          <div className="flex items-center gap-3 px-5 py-4">
            <Search className="w-5 h-5 text-white/40 shrink-0" />
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 bg-transparent text-white text-lg placeholder:text-white/30 outline-none font-light"
              readOnly={isRunning}
            />
            {isRunning && (
              <Loader2 className="w-5 h-5 text-[#fa5a19] animate-spin shrink-0" />
            )}
          </div>
        </div>
      </div>

      {/* Demo Query Pills */}
      <div className="flex flex-wrap gap-2 mb-8 justify-center">
        {DEMO_QUERIES.map((q, i) => (
          <button
            key={i}
            onClick={() => runDemo(i)}
            disabled={isRunning}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              selectedQuery === i
                ? "bg-[#fa5a19] text-white shadow-lg shadow-[#fa5a19]/25"
                : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80 border border-white/10"
            } ${isRunning ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
          >
            {q.query}
          </button>
        ))}
      </div>

      {/* Pipeline Steps */}
      {(isRunning || showResults) && (
        <div className="bg-[#111111] border border-white/5 rounded-2xl p-6 mb-6">
          <div className="space-y-3">
            {steps.map((step, i) => {
              const status = getStepStatus(i);
              return (
                <div
                  key={i}
                  className={`flex items-center gap-3 transition-all duration-300 ${
                    status === "done"
                      ? "text-[#3ddc84]"
                      : status === "active"
                      ? "text-[#fa5a19]"
                      : "text-white/20"
                  }`}
                >
                  {status === "done" ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                  ) : status === "active" ? (
                    <Loader2 className="w-4 h-4 animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-white/20 shrink-0" />
                  )}
                  <span className="text-sm font-medium">{step.label}</span>
                  {status === "done" && i === currentStep - 1 && isRunning && (
                    <span className="text-xs text-white/30 ml-auto">done</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Results */}
      {showResults && (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Sources */}
          <div className="bg-[#111111] border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-white/60 text-sm font-medium uppercase tracking-wider">Sources Found</h4>
              <span className="text-[#fa5a19] text-2xl font-bold">{demo.sources}</span>
            </div>
            <div className="flex gap-2 flex-wrap">
              {Array.from({ length: Math.min(demo.sources, 8) }).map((_, i) => (
                <div
                  key={i}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-lg text-xs text-white/50"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>source-{i + 1}.com</span>
                </div>
              ))}
              {demo.sources > 8 && (
                <div className="px-3 py-1.5 bg-white/5 rounded-lg text-xs text-white/30">
                  +{demo.sources - 8} more
                </div>
              )}
            </div>
          </div>

          {/* Entities */}
          <div className="bg-[#111111] border border-white/5 rounded-2xl p-6">
            <h4 className="text-white/60 text-sm font-medium uppercase tracking-wider mb-4">
              Entities Extracted
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {demo.entities.map((ent, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 bg-white/[0.02] rounded-xl border border-white/5"
                >
                  <div className="w-8 h-8 rounded-lg bg-[#fa5a19]/10 flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-[#fa5a19] text-xs font-bold">
                      {ent.type.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="text-white text-sm font-medium">{ent.name}</div>
                    <div className="text-white/40 text-xs mt-0.5">{ent.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Report */}
          <div className="bg-[#111111] border border-white/5 rounded-2xl p-6">
            <h4 className="text-white/60 text-sm font-medium uppercase tracking-wider mb-4">
              Generated Report
            </h4>
            <div className="text-white/80 text-sm leading-relaxed whitespace-pre-line">
              {demo.report}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
