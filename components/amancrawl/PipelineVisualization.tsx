"use client";

import { useEffect, useRef, useState } from "react";
import { Globe, FileText, GitBranch, Brain, Cpu, Zap } from "lucide-react";

const INPUT_SOURCES = [
  { label: "Websites", icon: <Globe className="w-4 h-4" /> },
  { label: "Documentation", icon: <FileText className="w-4 h-4" /> },
  { label: "GitHub", icon: <GitBranch className="w-4 h-4" /> },
  { label: "PDFs", icon: <FileText className="w-4 h-4" /> },
  { label: "APIs", icon: <Zap className="w-4 h-4" /> },
  { label: "Browser Sessions", icon: <Globe className="w-4 h-4" /> },
];

const PIPELINE_STEPS = [
  { label: "Discover", description: "Find relevant sources" },
  { label: "Crawl", description: "Access content at scale" },
  { label: "Extract", description: "Pull structured data" },
  { label: "Research", description: "Reason over information" },
  { label: "Monitor", description: "Track changes over time" },
];

const OUTPUT_TARGETS = [
  "AI Agents",
  "RAG Systems",
  "Copilots",
  "Workflows",
  "Knowledge Graphs",
  "Research Reports",
];

export default function PipelineVisualization() {
  const [visibleSteps, setVisibleSteps] = useState<number>(0);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            let step = 0;
            const interval = setInterval(() => {
              step++;
              setVisibleSteps(step);
              if (step >= PIPELINE_STEPS.length) clearInterval(interval);
            }, 300);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={sectionRef} className="w-full max-w-5xl mx-auto py-20">
      <div className="text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
          From Information to Intelligence
        </h2>
        <p className="text-white/50 text-lg max-w-2xl mx-auto">
          AmanCrawl transforms raw web data into structured, agent-ready knowledge
          through a multi-stage intelligence pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-8 items-start">
        {/* Input Sources */}
        <div className="space-y-3">
          <div className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-4 text-center md:text-right">
            Input Sources
          </div>
          {INPUT_SOURCES.map((source, i) => (
            <div
              key={i}
              className="flex items-center gap-3 p-3 bg-white/[0.03] border border-white/5 rounded-xl
                         hover:bg-white/[0.06] hover:border-white/10 transition-all duration-300
                         md:flex-row-reverse md:text-right"
            >
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-white/40 shrink-0">
                {source.icon}
              </div>
              <span className="text-white/70 text-sm font-medium">{source.label}</span>
            </div>
          ))}
        </div>

        {/* Center Pipeline */}
        <div className="flex flex-col items-center gap-0 py-8">
          {/* AmanCrawl Hub */}
          <div className="relative z-10 w-20 h-20 rounded-2xl bg-gradient-to-br from-[#fa5a19] to-[#ff8c42]
                          flex items-center justify-center shadow-2xl shadow-[#fa5a19]/30 mb-2">
            <Brain className="w-9 h-9 text-white" />
          </div>
          <div className="text-white font-bold text-lg mb-8">AmanCrawl</div>

          {/* Pipeline Steps */}
          <div className="flex flex-col items-center">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={i} className="flex flex-col items-center">
                {/* Connector line */}
                <div
                  className={`w-px h-8 transition-all duration-500 ${
                    visibleSteps > i ? "bg-[#fa5a19]" : "bg-white/10"
                  }`}
                />
                {/* Step circle */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold
                              transition-all duration-500 ${
                                visibleSteps > i
                                  ? "bg-[#fa5a19] text-white shadow-lg shadow-[#fa5a19]/30 scale-100"
                                  : "bg-white/5 text-white/20 scale-90"
                              }`}
                >
                  {i + 1}
                </div>
                {/* Step label */}
                <div
                  className={`mt-1 mb-1 text-center transition-all duration-500 ${
                    visibleSteps > i ? "opacity-100" : "opacity-30"
                  }`}
                >
                  <div className="text-white text-sm font-semibold">{step.label}</div>
                  <div className="text-white/40 text-xs">{step.description}</div>
                </div>
              </div>
            ))}
            {/* Final connector */}
            <div
              className={`w-px h-8 transition-all duration-500 ${
                visibleSteps >= PIPELINE_STEPS.length ? "bg-[#3ddc84]" : "bg-white/10"
              }`}
            />
            {/* Output indicator */}
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${
                visibleSteps >= PIPELINE_STEPS.length
                  ? "bg-[#3ddc84] text-white shadow-lg shadow-[#3ddc84]/30"
                  : "bg-white/5 text-white/20"
              }`}
            >
              <Cpu className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Output Targets */}
        <div className="space-y-3">
          <div className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-4">
            Output Targets
          </div>
          {OUTPUT_TARGETS.map((target, i) => (
            <div
              key={i}
              className={`flex items-center gap-3 p-3 bg-white/[0.03] border border-white/5 rounded-xl
                          hover:bg-white/[0.06] hover:border-white/10 transition-all duration-300
                          ${visibleSteps >= PIPELINE_STEPS.length ? "opacity-100 translate-x-0" : "opacity-30 translate-x-2"}`}
              style={{ transitionDelay: `${i * 100}ms` }}
            >
              <div className="w-2 h-2 rounded-full bg-[#3ddc84] shrink-0" />
              <span className="text-white/70 text-sm font-medium">{target}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
