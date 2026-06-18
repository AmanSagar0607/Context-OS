"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loadAuthUser, isAuthenticated, clearAuthSession } from "@/lib/auth";
import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";
import UsageCounter from "@/components/UsageCounter";
import {
  fetchDashboardStats,
  fetchRecentConversations,
  fetchRecentMemories,
  type DashboardStats,
  type ConversationItem,
  type MemoryItem,
} from "@/services/dashboard";
import {
  Search,
  FileSearch,
  Globe2,
  Map,
  Loader2,
  ArrowRight,
  LayoutDashboard,
  User,
  Layers,
  Brain,
  FileText,
  Bot,
  Database,
  Globe,
  Clock,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import type { AuthUser } from "@/lib/types";

type Platform = "lab" | "crawl" | "both";

const TOOLS = [
  { id: "search", label: "Search", icon: Search, color: "emerald", scope: "crawl:search", placeholder: "e.g. open source vector databases 2025" },
  { id: "scrape", label: "Scrape", icon: FileSearch, color: "violet", scope: "crawl:scrape", placeholder: "e.g. https://example.com/products" },
  { id: "map", label: "Map", icon: Map, color: "amber", scope: "crawl:map", placeholder: "e.g. https://docs.crewai.com" },
  { id: "crawl", label: "Crawl", icon: Globe2, color: "green", scope: "crawl:crawl", placeholder: "e.g. https://docs.crewai.com" },
] as const;

const PLAN_FEATURES = {
  free: { label: "Free", artifacts: 5, crawlJobs: 20, memories: 100, pagesCrawled: 500, workspaces: 1, agents: 0, conversations: 20 },
  pro: { label: "Pro", artifacts: 100, crawlJobs: 500, memories: 5000, pagesCrawled: 20000, workspaces: 10, agents: 5, conversations: 200 },
  team: { label: "Team", artifacts: -1, crawlJobs: -1, memories: -1, pagesCrawled: -1, workspaces: -1, agents: -1, conversations: -1 },
  enterprise: { label: "Enterprise", artifacts: -1, crawlJobs: -1, memories: -1, pagesCrawled: -1, workspaces: -1, agents: -1, conversations: -1 },
} as const;

const POLL_INTERVAL = 30000; // 30 seconds

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [platform, setPlatform] = useState<Platform>("both");
  const [activeTab, setActiveTab] = useState("search");
  const [inputValue, setInputValue] = useState("");
  const [toolLoading, setToolLoading] = useState(false);
  const [toolResult, setToolResult] = useState<string | null>(null);
  const [toolError, setToolError] = useState<string | null>(null);

  // Real data states
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [fetchErrors, setFetchErrors] = useState<string[]>([]);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login?redirect=/dashboard");
      return;
    }
    setUser(loadAuthUser());
  }, [router]);

  // Fetch real data — re-runs when platform changes
  const loadData = useCallback(async (showLoading = true) => {
    if (!user) return;
    if (showLoading) setLoadingData(true);
    setFetchErrors([]);
    try {
      const [s, c, m] = await Promise.all([
        fetchDashboardStats(platform).catch((e) => { setFetchErrors((prev) => [...prev, `stats: ${e.message}`]); return null; }),
        platform === "crawl" ? Promise.resolve([]) : fetchRecentConversations(8).catch((e) => { setFetchErrors((prev) => [...prev, `conversations: ${e.message}`]); return []; }),
        platform === "crawl" ? Promise.resolve([]) : fetchRecentMemories(5).catch((e) => { setFetchErrors((prev) => [...prev, `memories: ${e.message}`]); return []; }),
      ]);
      if (s) setStats(s);
      setConversations(c);
      setMemories(m);
      setLastRefresh(new Date());
    } finally {
      setLoadingData(false);
    }
  }, [user, platform]);

  // Initial load + re-fetch on platform change
  useEffect(() => {
    loadData(true);
  }, [loadData]);

  // Auto-refresh polling
  useEffect(() => {
    if (!user) return;
    pollRef.current = setInterval(() => loadData(false), POLL_INTERVAL);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [user, loadData]);

  const plan = (user?.plan as keyof typeof PLAN_FEATURES) || "free";
  const features = PLAN_FEATURES[plan];
  const initials = user
    ? (user.full_name || user.email || "U").split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : "U";
  const displayName = user?.full_name || user?.username || user?.email?.split("@")[0] || "User";

  const maxVal = (v: number, max: number) => max === -1 ? "∞" : `${v}/${max}`;

  const runTool = useCallback(async () => {
    const val = inputValue.trim();
    if (!val || toolLoading) return;
    setToolLoading(true);
    setToolResult(null);
    setToolError(null);
    try {
      const body = activeTab === "search"
        ? { query: val, num_results: 5 }
        : { url: val, formats: ["markdown"], timeout: 30 };
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/amancrawl/${activeTab}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Request failed" }));
        if (res.status === 401) { clearAuthSession(); router.replace("/login?redirect=/dashboard"); return; }
        throw new Error(err.detail || "Request failed");
      }
      setToolResult(JSON.stringify(await res.json(), null, 2));
      // Refresh stats after successful tool run
      loadData(false);
    } catch (e: unknown) {
      setToolError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setToolLoading(false);
    }
  }, [inputValue, activeTab, toolLoading, router, loadData]);

  if (!user) return null;

  // Filter stats based on platform
  const showConversations = platform !== "crawl";
  const showCrawl = platform !== "lab";

  return (
    <div className="flex min-h-screen bg-white dark:bg-[#0a0a0a] text-[#201510] dark:text-white">
      {/* ── SIDEBAR ── */}
      <aside className="w-[220px] min-h-screen bg-[#faf7f2] dark:bg-[#13151a] border-r border-[#e5e7eb] dark:border-white/[0.07] flex flex-col py-5 flex-shrink-0 sticky top-0 h-screen">
        <div className="px-4 pb-5 border-b border-[#e5e7eb] dark:border-white/[0.07] mb-2">
          <div className="text-[17px] font-bold tracking-tight">
            <span className="text-[#6C63FF]">A</span>man Platform
          </div>
          <div className="text-[10px] uppercase tracking-widest text-[#999] dark:text-[#555a6b] mt-1 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#6C63FF]" />
            AgentLab + AmanCrawl
          </div>
        </div>

        <nav className="flex-1 px-2 space-y-0.5">
          <div className="text-[10px] uppercase tracking-widest text-[#bbb] dark:text-[#555a6b] px-3 pt-2 pb-1">General</div>
          <SideLink icon={<LayoutDashboard className="w-4 h-4" />} label="Dashboard" active />
          <SideLink icon={<User className="w-4 h-4" />} label="Profile" />
          <SideLink icon={<Layers className="w-4 h-4" />} label="Workspaces" badge={features.workspaces === -1 ? "∞" : features.workspaces} />

          <div className="text-[10px] uppercase tracking-widest text-[#bbb] dark:text-[#555a6b] px-3 pt-4 pb-1">AgentLab</div>
          <SideLink icon={<Brain className="w-4 h-4" />} label="Memory" badge={stats?.memory_entries ?? 0} />
          <SideLink icon={<FileText className="w-4 h-4" />} label="Artifacts" badge={stats?.artifacts ?? 0} />
          <SideLink icon={<Bot className="w-4 h-4" />} label="Agents" badge={features.agents} locked={features.agents === 0} />

          <div className="text-[10px] uppercase tracking-widest text-[#bbb] dark:text-[#555a6b] px-3 pt-4 pb-1">AmanCrawl</div>
          <SideLink icon={<Search className="w-4 h-4" />} label="Search" onClick={() => setActiveTab("search")} />
          <SideLink icon={<Globe className="w-4 h-4" />} label="Crawl" onClick={() => setActiveTab("crawl")} />
          <SideLink icon={<FileSearch className="w-4 h-4" />} label="Scrape" onClick={() => setActiveTab("scrape")} />
          <SideLink icon={<Map className="w-4 h-4" />} label="Map" onClick={() => setActiveTab("map")} />
          <SideLink icon={<Database className="w-4 h-4" />} label="Crawl History" badge={stats?.crawl_jobs ?? 0} />
        </nav>

        <div className="mt-auto px-2 pt-3 border-t border-[#e5e7eb] dark:border-white/[0.07]">
          <Link href="/dashboard" className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-[#f0ece6] dark:hover:bg-white/5 transition">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#6C63FF] to-[#00C9A7] flex items-center justify-center text-[10px] font-semibold text-white shrink-0">{initials}</div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium truncate">{displayName}</div>
              <div className="text-[10px] text-[#999] dark:text-[#555a6b]">{features.label} plan</div>
            </div>
          </Link>
        </div>
      </aside>

      {/* ── MAIN ── */}
      <main className="flex-1 overflow-y-auto p-7">
        {/* Topbar */}
        <div className="flex items-center gap-3 mb-7">
          <div className="flex-1">
            <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>
            <p className="text-sm text-[#999] dark:text-[#555a6b] mt-0.5">
              {new Date().toLocaleDateString("en-US", { weekday: "long", day: "numeric", month: "long", year: "numeric" })} · All systems operational
              {lastRefresh && (
                <span className="ml-2 text-[10px] text-[#bbb] dark:text-[#555a6b]">
                  · Updated {lastRefresh.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>

          <button
            onClick={() => loadData(false)}
            disabled={loadingData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#e5e7eb] dark:border-white/[0.07] text-xs text-[#999] hover:text-[#666] dark:hover:text-white/60 transition"
            title="Refresh now"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingData ? "animate-spin" : ""}`} />
            Refresh
          </button>

          <div className="flex gap-1.5 bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] p-1 rounded-xl">
            {([["lab", "AgentLab", "#6C63FF"], ["crawl", "AmanCrawl", "#00C9A7"], ["both", "Both", "#999"]] as const).map(([p, label, color]) => (
              <button key={p} onClick={() => setPlatform(p)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${platform === p ? "bg-white dark:bg-white/10 shadow-sm" : "text-[#999] hover:text-[#666]"}`} style={platform === p ? { color } : undefined}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
                {label}
              </button>
            ))}
          </div>

          <AnimatedThemeToggler className="w-8 h-8 flex items-center justify-center rounded-lg border border-[#e5e7eb] dark:border-white/[0.07] text-[#999] dark:text-[#555a6b] hover:text-[#201510] dark:hover:text-white transition" variant="circle" />

          <Link href="/dashboard" className="flex items-center gap-2 bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-lg px-2.5 py-1.5 transition hover:border-[#6C63FF]/30">
            <div className="w-5.5 h-5.5 rounded-full bg-gradient-to-br from-[#6C63FF] to-[#00C9A7] flex items-center justify-center text-[8px] font-semibold text-white">{initials}</div>
            <span className="text-xs font-medium hidden sm:inline">{displayName}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#00C9A7]/10 text-[#00C9A7] font-semibold">{features.label}</span>
          </Link>
        </div>

        {/* ── FETCH ERRORS ── */}
        {fetchErrors.length > 0 && (
          <div className="mb-4 flex items-start gap-2 rounded-xl border border-amber-200 dark:border-amber-500/20 bg-amber-50 dark:bg-amber-500/5 p-3">
            <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-700 dark:text-amber-400">
              <span className="font-medium">Some data couldn&apos;t load:</span>
              <ul className="mt-1 space-y-0.5">
                {fetchErrors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          </div>
        )}

        {/* ── STATS ── */}
        <div className={`grid gap-3 mb-6 ${showConversations && showCrawl ? "grid-cols-4" : showConversations || showCrawl ? "grid-cols-3" : "grid-cols-2"}`}>
          {showConversations && (
            <>
              <StatCard color="#6C63FF" label="Conversations" value={stats?.conversations ?? 0} max={features.conversations} loading={loadingData} />
              <StatCard color="#3ddc84" label="Memory entries" value={stats?.memory_entries ?? 0} max={features.memories} loading={loadingData} />
              <StatCard color="#f0a500" label="Artifacts" value={stats?.artifacts ?? 0} max={features.artifacts} loading={loadingData} />
            </>
          )}
          {showCrawl && (
            <>
              <StatCard color="#00C9A7" label="Scrapes today" value={stats?.crawl_scrape?.used ?? 0} max={stats?.crawl_scrape?.limit ?? 0} loading={loadingData} />
              {!showConversations && (
                <>
                  <StatCard color="#6C63FF" label="Searches today" value={stats?.crawl_search?.used ?? 0} max={stats?.crawl_search?.limit ?? 0} loading={loadingData} />
                  <StatCard color="#f59e0b" label="Maps today" value={stats?.crawl_map?.used ?? 0} max={stats?.crawl_map?.limit ?? 0} loading={loadingData} />
                </>
              )}
              <StatCard color="#8b5cf6" label="Crawls this month" value={stats?.crawl_crawl?.used ?? 0} max={stats?.crawl_crawl?.limit ?? 0} loading={loadingData} />
            </>
          )}
        </div>

        {/* ── USAGE QUOTA ── */}
        {showCrawl && (
          <div className="mb-6">
            <UsageCounter
              resources={["crawl:scrape", "crawl:search", "crawl:map", "crawl:crawl"]}
              compact
            />
          </div>
        )}

        {/* ── QUICK TOOL ── */}
        {showCrawl && (
          <div className="bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-2xl p-4 mb-6">
            <div className="flex gap-1 mb-3 border-b border-[#e5e7eb] dark:border-white/[0.07] pb-2.5">
              {TOOLS.map((t) => (
                <button key={t.id} onClick={() => setActiveTab(t.id)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${activeTab === t.id ? "bg-[#00C9A7]/10 text-[#00C9A7]" : "text-[#999] hover:text-[#666] dark:hover:text-white/60"}`}>
                  <t.icon className="w-3.5 h-3.5" />
                  {t.label}
                </button>
              ))}
            </div>
            <div className="flex gap-2.5 items-center">
              <input value={inputValue} onChange={(e) => setInputValue(e.target.value)} onKeyDown={(e) => e.key === "Enter" && runTool()} placeholder={TOOLS.find((t) => t.id === activeTab)?.placeholder} className="flex-1 bg-white dark:bg-[#0a0a0a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-xl px-4 py-2.5 text-sm font-mono outline-none focus:border-[#00C9A7] transition placeholder:text-[#bbb] dark:placeholder:text-white/30" />
              <button onClick={runTool} disabled={toolLoading || !inputValue.trim()} className="px-5 py-2.5 bg-[#00C9A7] text-[#0a0a0a] rounded-xl text-sm font-semibold transition hover:opacity-90 disabled:opacity-40 flex items-center gap-2">
                {toolLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                Run
              </button>
            </div>
            {toolError && <div className="mt-3 px-3 py-2 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-xs text-red-600 dark:text-red-400">{toolError}</div>}
            {toolResult && <pre className="mt-3 p-3 rounded-xl bg-white dark:bg-[#0a0a0a] border border-[#e5e7eb] dark:border-white/[0.07] text-[11px] text-[#666] dark:text-white/60 font-mono max-h-48 overflow-auto whitespace-pre-wrap">{toolResult}</pre>}
          </div>
        )}

        {/* ── TWO COL: Conversations + Memories ── */}
        {showConversations && (
          <div className="grid grid-cols-2 gap-4 mb-6">
            {/* Recent Conversations */}
            <Panel title="Recent Conversations" count={conversations.length} color="#6C63FF" icon={<MessageIcon />}>
              {loadingData ? (
                <LoadingSkeleton rows={4} />
              ) : conversations.length === 0 ? (
                <EmptyState message="No conversations yet" sub="Start a chat to see your history here" />
              ) : (
                conversations.map((c) => (
                  <Link key={c.id} href={`/chat?id=${c.id}`} className="flex items-center gap-3 px-4 py-2.5 hover:bg-[#f0ece6] dark:hover:bg-white/5 transition border-b border-[#e5e7eb] dark:border-white/[0.07] last:border-0">
                    <div className="w-8 h-8 rounded-lg bg-[#6C63FF]/10 flex items-center justify-center shrink-0">
                      <MessageIcon className="w-4 h-4 text-[#6C63FF]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{c.title || "Untitled"}</div>
                      <div className="text-[11px] text-[#999] dark:text-[#555a6b] mt-0.5">{timeAgo(c.updated_at)}</div>
                    </div>
                  </Link>
                ))
              )}
            </Panel>

            {/* Recent Memories */}
            <Panel title="Recent Memory" count={memories.length} color="#00C9A7" icon={<Brain className="w-3.5 h-3.5" />}>
              {loadingData ? (
                <LoadingSkeleton rows={4} />
              ) : memories.length === 0 ? (
                <EmptyState message="No memories yet" sub="Your profile facts will appear here" />
              ) : (
                memories.map((m, i) => (
                  <div key={i} className="flex gap-3 px-4 py-2.5 border-b border-[#e5e7eb] dark:border-white/[0.07] last:border-0">
                    <div className="w-0.5 rounded-full bg-[#00C9A7]/40 shrink-0 mt-1" style={{ minHeight: 32 }} />
                    <div className="min-w-0">
                      <div className="text-xs font-medium text-[#666] dark:text-white/70">{m.key.replace(/_/g, " ")}</div>
                      <div className="text-[11px] text-[#999] dark:text-[#555a6b] mt-0.5 line-clamp-2">{m.content}</div>
                      <div className="text-[10px] text-[#bbb] dark:text-[#555a6b] mt-1">{timeAgo(m.updated_at)}</div>
                    </div>
                  </div>
                ))
              )}
            </Panel>
          </div>
        )}
      </main>
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────

function SideLink({ icon, label, active, badge, locked, onClick }: { icon: React.ReactNode; label: string; active?: boolean; badge?: number | string; locked?: boolean; onClick?: () => void }) {
  return (
    <button onClick={onClick} disabled={locked} className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] transition ${active ? "bg-[#6C63FF]/10 text-[#6C63FF] font-medium" : "text-[#666] dark:text-[#8a8f9e] hover:bg-[#f0ece6] dark:hover:bg-white/5"} ${locked ? "opacity-40 cursor-not-allowed" : ""}`}>
      <span className="shrink-0 opacity-70">{icon}</span>
      <span className="flex-1 text-left">{label}</span>
      {badge !== undefined && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#f0ece6] dark:bg-white/5 text-[#999] dark:text-[#555a6b]">{badge}</span>}
    </button>
  );
}

function StatCard({ color, label, value, max, loading }: { color: string; label: string; value: number; max: number; loading: boolean }) {
  const display = max === -1 ? "∞" : `${value}/${max}`;
  return (
    <div className="bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-xl p-4">
      <div className="flex items-center gap-1.5 text-[11px] text-[#999] dark:text-[#555a6b] uppercase tracking-wider mb-2">
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
        {label}
      </div>
      {loading ? (
        <div className="h-7 w-12 bg-[#e5e7eb] dark:bg-white/10 rounded animate-pulse" />
      ) : (
        <div className="text-2xl font-bold tracking-tight">{value}</div>
      )}
      <div className="text-[11px] text-[#bbb] dark:text-[#555a6b] mt-1">{loading ? "..." : display}</div>
    </div>
  );
}

function Panel({ title, count, color, icon, children }: { title: string; count: number; color: string; icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-2xl overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#e5e7eb] dark:border-white/[0.07]">
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
        {icon}
        <span className="text-xs font-semibold text-[#666] dark:text-[#8a8f9e] uppercase tracking-wider">{title}</span>
        <span className="ml-auto text-[10px] text-[#999] dark:text-[#555a6b] bg-white dark:bg-[#0a0a0a] px-2 py-0.5 rounded-full border border-[#e5e7eb] dark:border-white/[0.07]">{count}</span>
      </div>
      <div className="max-h-72 overflow-y-auto">{children}</div>
    </div>
  );
}

function LoadingSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="p-4 space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#e5e7eb] dark:bg-white/10 animate-pulse" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3 w-3/4 rounded bg-[#e5e7eb] dark:bg-white/10 animate-pulse" />
            <div className="h-2.5 w-1/2 rounded bg-[#e5e7eb] dark:bg-white/10 animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ message, sub }: { message: string; sub: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <div className="text-sm font-medium text-[#666] dark:text-white/70">{message}</div>
      <div className="text-[11px] text-[#999] dark:text-[#555a6b] mt-1">{sub}</div>
    </div>
  );
}

function MessageIcon({ className }: { className?: string }) {
  return <FileText className={className} />;
}

function timeAgo(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  } catch {
    return dateStr;
  }
}
