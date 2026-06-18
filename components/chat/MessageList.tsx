"use client";

import type { ReactNode } from "react";
import {
  Clipboard,
  Copy,
  Edit3,
  Flag,
  RefreshCw,
  Share,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { Message } from "@/components/chat/types";

interface Props {
  messages: Message[];
  isTyping: boolean;
  onCopy?: (content: string) => void;
  onEdit?: (message: Message) => void;
  onRegenerate?: (message: Message) => void;
  onSources?: (message: Message) => void;
}

export default function MessageList({
  messages,
  isTyping,
  onCopy,
  onEdit,
  onRegenerate,
  onSources,
}: Props) {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
      {messages.map((msg) => (
        (() => {
          const isHighlightedAnswer =
            msg.role === "assistant" && msg.emphasis === "highlight";
          const messageClasses =
            msg.role === "user"
              ? "bg-[#f1e8dc] text-[#201510] dark:bg-slate-800 dark:text-white"
              : isHighlightedAnswer
                ? "border border-emerald-500/25 bg-emerald-500/8 text-[#201510] shadow-[0_0_0_1px_rgba(16,185,129,0.08)] dark:text-white"
                : "text-[#201510] dark:text-white";

          return (
        <div
          key={msg.id}
          className={`group/message flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
        >
          {msg.role === "assistant" && (
            <div className="mt-1 h-6 w-6 flex-shrink-0 rounded-full bg-gradient-to-br from-[#e67d2b] to-[#f3b36d] dark:from-violet-500 dark:to-cyan-400" />
          )}
          <div className={`flex max-w-[82%] flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div
              className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${messageClasses}`}
            >
              {msg.badge ? (
                <div className="mb-2 inline-flex rounded-full border border-emerald-400/25 bg-emerald-500/12 px-2 py-0.5 text-[11px] font-medium uppercase tracking-[0.14em] text-emerald-700 dark:text-emerald-200">
                  {msg.badge}
                </div>
              ) : null}
              <div className="whitespace-pre-wrap">{msg.content}</div>
            </div>

            {msg.role === "user" ? (
              <div className="mt-1.5 flex items-center gap-1 opacity-0 transition group-hover/message:opacity-100">
                <MessageActionButton
                  label="Copy question"
                  onClick={() => onCopy?.(msg.content)}
                >
                  <Copy className="h-3.5 w-3.5" />
                </MessageActionButton>
                <MessageActionButton
                  label="Edit question"
                  onClick={() => onEdit?.(msg)}
                >
                  <Edit3 className="h-3.5 w-3.5" />
                </MessageActionButton>
              </div>
            ) : (
              <div className="mt-2 flex flex-wrap items-center gap-1.5 opacity-0 transition group-hover/message:opacity-100">
                <MessageActionButton
                  label="Copy answer"
                  onClick={() => onCopy?.(msg.content)}
                >
                  <Clipboard className="h-3.5 w-3.5" />
                </MessageActionButton>
                <MessageActionButton label="Good response">
                  <ThumbsUp className="h-3.5 w-3.5" />
                </MessageActionButton>
                <MessageActionButton label="Bad response">
                  <ThumbsDown className="h-3.5 w-3.5" />
                </MessageActionButton>
                <MessageActionButton label="Share answer">
                  <Share className="h-3.5 w-3.5" />
                </MessageActionButton>
                <MessageActionButton
                  label="Regenerate answer"
                  onClick={() => onRegenerate?.(msg)}
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                </MessageActionButton>
                <MessageActionButton label="Report answer">
                  <Flag className="h-3.5 w-3.5" />
                </MessageActionButton>
                <button
                  type="button"
                  onClick={() => onSources?.(msg)}
                  className="ml-1 inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium text-[#7a5b49] transition hover:bg-[#f1e8dc] hover:text-[#201510] dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
                >
                  <Clipboard className="h-3.5 w-3.5" />
                  Sources
                </button>
              </div>
            )}
          </div>
        </div>
          );
        })()
      ))}

      {isTyping && (
        <div className="flex gap-3">
          <div className="mt-1 h-6 w-6 flex-shrink-0 rounded-full bg-gradient-to-br from-[#e67d2b] to-[#f3b36d] dark:from-violet-500 dark:to-cyan-400" />
          <div className="flex items-center gap-1 rounded-2xl px-4 py-3">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#a18672] [animation-delay:0ms] dark:bg-slate-400" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#a18672] [animation-delay:150ms] dark:bg-slate-400" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#a18672] [animation-delay:300ms] dark:bg-slate-400" />
          </div>
        </div>
      )}
    </div>
  );
}

function MessageActionButton({
  label,
  children,
  onClick,
}: {
  label: string;
  children: ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className="flex h-7 w-7 items-center justify-center rounded-lg text-[#7a5b49] transition hover:bg-[#f1e8dc] hover:text-[#201510] dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
    >
      {children}
    </button>
  );
}
