"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loadAuthUser, isAuthenticated, buildAuthHeaders } from "@/lib/auth";
import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";
import {
  Users,
  Activity,
  Database,
  Settings,
  Shield,
  BarChart3,
  ArrowLeft,
  Search,
  Loader2,
  RefreshCw,
  User,
  Mail,
  Calendar,
  Crown,
} from "lucide-react";
import type { AuthUser } from "@/lib/types";

type AdminTab = "users" | "system" | "settings";

interface UserRecord {
  id: string;
  email: string;
  plan: string;
  created_at: string;
}

interface SystemStats {
  users: number;
  conversations: number;
  memory_entries: number;
  crawl_jobs: number;
  kg_entities: number;
  kg_relationships: number;
  postgres_size: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [tab, setTab] = useState<AdminTab>("users");
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login?redirect=/admin");
      return;
    }
    const u = loadAuthUser();
    setUser(u);
    // For now, allow any authenticated user to view admin
    // In production, check if user is admin
  }, [router]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const headers = buildAuthHeaders();

      // Fetch users from the admin endpoint
      const usersRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/dashboard/stats`, { headers });
      if (usersRes.ok) {
        const data = await usersRes.json();
        setStats(data);
      }
    } catch (e) {
      console.error("Failed to load admin data:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) loadData();
  }, [user, loadData]);

  if (!user) return null;

  const filteredUsers = users.filter(
    (u) =>
      u.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-white dark:bg-[#0a0a0a]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-[#e5e7eb] dark:border-white/[0.07] animate-slide-up-fade">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center gap-4">
          <Link href="/dashboard" className="flex items-center gap-2 text-[#999] hover:text-[#666] dark:hover:text-white/60 transition text-sm">
            <ArrowLeft className="w-4 h-4" />
            Dashboard
          </Link>
          <div className="flex-1" />
          <h1 className="text-sm font-semibold flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#fa5a19]" />
            Admin Panel
          </h1>
          <div className="flex-1" />
          <AnimatedThemeToggler className="w-8 h-8 flex items-center justify-center rounded-lg border border-[#e5e7eb] dark:border-white/[0.07] text-[#999]" variant="circle" />
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] p-1 rounded-xl w-fit">
          {([["users", "Users", Users], ["system", "System", Activity], ["settings", "Settings", Settings]] as const).map(([id, label, Icon]) => (
            <button
              key={id}
              onClick={() => setTab(id as AdminTab)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition ${
                tab === id
                  ? "bg-white dark:bg-white/10 shadow-sm text-[#fa5a19]"
                  : "text-[#999] hover:text-[#666]"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>

        {/* System Stats */}
        {tab === "system" && (
          <div className="grid grid-cols-3 gap-4 mb-6 stagger-container">
            <SystemStatCard icon={<Users className="w-5 h-5" />} label="Total Users" value={stats?.users ?? 0} color="#fa5a19" />
            <SystemStatCard icon={<Database className="w-5 h-5" />} label="Memory Entries" value={stats?.memory_entries ?? 0} color="#3ddc84" />
            <SystemStatCard icon={<BarChart3 className="w-5 h-5" />} label="Conversations" value={stats?.conversations ?? 0} color="#8b5cf6" />
            <SystemStatCard icon={<Activity className="w-5 h-5" />} label="Crawl Jobs" value={stats?.crawl_jobs ?? 0} color="#00C9A7" />
            <SystemStatCard icon={<Database className="w-5 h-5" />} label="KG Entities" value={stats?.kg_entities ?? 0} color="#f59e0b" />
            <SystemStatCard icon={<Database className="w-5 h-5" />} label="KG Relationships" value={stats?.kg_relationships ?? 0} color="#ec4899" />
          </div>
        )}

        {/* Users Tab */}
        {tab === "users" && (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#999]" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search users..."
                  className="w-full bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-lg pl-9 pr-4 py-2 text-sm outline-none focus:border-[#fa5a19] transition"
                />
              </div>
              <button onClick={loadData} disabled={loading} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-[#e5e7eb] dark:border-white/[0.07] text-xs text-[#999] hover:text-[#666] transition">
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </button>
            </div>

            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-16 rounded-xl bg-[#faf7f2] dark:bg-[#13151a] animate-pulse" />
                ))}
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-10 h-10 text-[#ccc] dark:text-[#333] mx-auto mb-3" />
                <p className="text-sm text-[#999]">No users found</p>
                <p className="text-xs text-[#bbb] dark:text-[#555a6b] mt-1">
                  User management will appear here when more users sign up
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredUsers.map((u) => (
                  <div key={u.id} className="flex items-center gap-4 p-4 bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-xl hover:border-[#fa5a19]/20 transition">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#fa5a19] to-[#3ddc84] flex items-center justify-center text-xs font-bold text-white">
                      {u.email?.[0]?.toUpperCase() || "U"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{u.email}</div>
                      <div className="text-[11px] text-[#999] mt-0.5 flex items-center gap-2">
                        <span className="font-mono">{u.id.slice(0, 8)}...</span>
                        <span>·</span>
                        <span>{u.created_at ? new Date(u.created_at).toLocaleDateString() : "N/A"}</span>
                      </div>
                    </div>
                    <span className={`text-[10px] px-2 py-1 rounded-full font-semibold ${
                      u.plan === "pro" || u.plan === "enterprise"
                        ? "bg-[#fa5a19]/10 text-[#fa5a19]"
                        : "bg-[#f0ece6] dark:bg-white/5 text-[#999]"
                    }`}>
                      {u.plan || "free"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Settings Tab */}
        {tab === "settings" && (
          <div className="space-y-4 stagger-container">
            <SettingsCard title="OAuth Providers" description="Configure Google and GitHub OAuth">
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-[#faf7f2] dark:bg-[#13151a] rounded-lg border border-[#e5e7eb] dark:border-white/[0.07]">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-white dark:bg-white/10 flex items-center justify-center border border-[#e5e7eb] dark:border-white/[0.07]">
                      <span className="text-sm font-bold">G</span>
                    </div>
                    <div>
                      <div className="text-sm font-medium">Google</div>
                      <div className="text-[11px] text-[#999]">OAuth 2.0 provider</div>
                    </div>
                  </div>
                  <span className="text-[10px] px-2 py-1 rounded-full bg-[#f0ece6] dark:bg-white/5 text-[#999]">
                    Configure in .env
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-[#faf7f2] dark:bg-[#13151a] rounded-lg border border-[#e5e7eb] dark:border-white/[0.07]">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-white dark:bg-white/10 flex items-center justify-center border border-[#e5e7eb] dark:border-white/[0.07]">
                      <span className="text-sm font-bold">G</span>
                    </div>
                    <div>
                      <div className="text-sm font-medium">GitHub</div>
                      <div className="text-[11px] text-[#999]">OAuth 2.0 provider</div>
                    </div>
                  </div>
                  <span className="text-[10px] px-2 py-1 rounded-full bg-[#f0ece6] dark:bg-white/5 text-[#999]">
                    Configure in .env
                  </span>
                </div>
              </div>
            </SettingsCard>

            <SettingsCard title="Payment Provider" description="BaseUPI integration for zero-commission UPI payments">
              <div className="p-3 bg-[#faf7f2] dark:bg-[#13151a] rounded-lg border border-[#e5e7eb] dark:border-white/[0.07]">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#3ddc84]/10 flex items-center justify-center">
                    <Crown className="w-4 h-4 text-[#3ddc84]" />
                  </div>
                  <div>
                    <div className="text-sm font-medium">BaseUPI</div>
                    <div className="text-[11px] text-[#999]">Zero-commission UPI payments · Instant settlement</div>
                  </div>
                </div>
              </div>
            </SettingsCard>

            <SettingsCard title="System Info" description="Backend configuration details">
              <div className="grid grid-cols-2 gap-3">
                <InfoItem label="Backend URL" value={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"} />
                <InfoItem label="Database" value="PostgreSQL 16 (Docker)" />
                <InfoItem label="Vector DB" value="Zilliz Cloud" />
                <InfoItem label="LLM Provider" value="OpenRouter" />
              </div>
            </SettingsCard>
          </div>
        )}
      </div>
    </div>
  );
}

function SystemStatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  return (
    <div className="bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-xl p-4 hover-lift">
      <div className="flex items-center gap-2 mb-3">
        <span style={{ color }}>{icon}</span>
        <span className="text-xs font-medium text-[#999] uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}

function SettingsCard({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <div className="bg-[#faf7f2] dark:bg-[#13151a] border border-[#e5e7eb] dark:border-white/[0.07] rounded-2xl p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold">{title}</h3>
        <p className="text-xs text-[#999] mt-0.5">{description}</p>
      </div>
      {children}
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 bg-white dark:bg-[#0a0a0a] rounded-lg border border-[#e5e7eb] dark:border-white/[0.07]">
      <div className="text-[10px] text-[#999] uppercase tracking-wider mb-1">{label}</div>
      <div className="text-xs font-mono">{value}</div>
    </div>
  );
}
