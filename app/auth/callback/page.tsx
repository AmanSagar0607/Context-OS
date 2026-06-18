"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { saveAuthSession, loadAuthUser } from "@/lib/auth";
import type { AuthSession, AuthUser } from "@/lib/types";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const userId = searchParams.get("user_id");
    const email = searchParams.get("email");
    const plan = searchParams.get("plan");

    if (!accessToken || !userId || !email) {
      setStatus("error");
      setError("Missing authentication parameters");
      return;
    }

    try {
      const session: AuthSession = {
        session_id: crypto.randomUUID(),
        access_token: accessToken,
        refresh_token: accessToken,
        expires_at: new Date(Date.now() + 7 * 86400000).toISOString(),
      };
      const user: AuthUser = { id: userId, email, plan: (plan || "free") as "free" | "pro" | "team" | "enterprise" };
      saveAuthSession(session, user);
      setStatus("success");
      setTimeout(() => router.replace("/dashboard"), 1000);
    } catch {
      setStatus("error");
      setError("Failed to save session");
    }
  }, [searchParams, router]);

  if (status === "loading") {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white dark:bg-[#0a0a0a]">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-[#fa5a19] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[#999]">Signing you in...</p>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white dark:bg-[#0a0a0a]">
        <div className="text-center max-w-sm">
          <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-500/10 flex items-center justify-center mx-auto mb-4">
            <span className="text-red-500 text-xl">!</span>
          </div>
          <h2 className="text-lg font-semibold mb-2">Authentication Failed</h2>
          <p className="text-sm text-[#999] mb-4">{error}</p>
          <button onClick={() => router.replace("/login")} className="px-4 py-2 bg-[#fa5a19] text-white rounded-lg text-sm font-medium hover:opacity-90 transition">
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-white dark:bg-[#0a0a0a]">
      <div className="text-center">
        <div className="w-10 h-10 rounded-full bg-[#3ddc84]/10 flex items-center justify-center mx-auto mb-4">
          <svg className="w-5 h-5 text-[#3ddc84]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p className="text-sm font-medium text-[#3ddc84]">Signed in successfully</p>
        <p className="text-xs text-[#999] mt-1">Redirecting to dashboard...</p>
      </div>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-white dark:bg-[#0a0a0a]">
        <div className="w-10 h-10 border-2 border-[#fa5a19] border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <CallbackContent />
    </Suspense>
  );
}
