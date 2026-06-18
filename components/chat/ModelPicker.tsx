"use client";

import { useEffect, useRef, useState } from "react";
import { MODELS, Model } from "@/components/chat/types";

interface Props {
  selected: Model | null;
  onSelect: (m: Model) => void;
}

export default function ModelPicker({ selected, onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  const current = selected ?? MODELS[0];

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const grouped = MODELS.filter((m) =>
    m.name.toLowerCase().includes(query.toLowerCase()),
  ).reduce<Record<string, Model[]>>((acc, m) => {
    const group = m.group ?? "Available";
    (acc[group] ??= []).push(m);
    return acc;
  }, {});

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="flex h-8 items-center gap-2 rounded-full border border-[#e5e7eb] bg-white/90 px-2.5 text-xs text-[#201510] transition hover:border-[#fa5a19]/30 hover:bg-[#fffdfa] hover:text-[#201510] dark:border-white/10 dark:bg-white/5 dark:text-slate-300 dark:hover:border-white/20 dark:hover:bg-white/10 dark:hover:text-white"
      >
        <ModelDot color={current.color} />
        <span className="max-w-32 truncate">{current.name}</span>
        <span className="text-[10px] leading-none text-[#a18672] dark:text-slate-500">v</span>
      </button>

      {open && (
        <div className="firecrawl-dropdown absolute bottom-10 left-0 z-50 w-72 rounded-[22px] p-2">
          <div className="px-1 pb-2 pt-1">
            <p className="text-[10px] uppercase tracking-[0.2em] text-[#a18672] dark:text-slate-500">
              Model
            </p>
          </div>
          <input
            id="model-search"
            name="model-search"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search models..."
            className="mb-2 h-9 w-full rounded-xl border border-[#e5e7eb] bg-white px-3 text-sm text-[#201510] outline-none placeholder:text-[#a18672] focus:border-[#fa5a19]/40 dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-[#fa5a19]/50"
          />
          {Object.entries(grouped).map(([group, models]) => (
            <div key={group} className="mb-2">
              <p className="mb-1 px-1 text-[10px] uppercase tracking-[0.2em] text-[#a18672] dark:text-slate-500">
                {group}
              </p>
              {models.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => {
                    onSelect(m);
                    setOpen(false);
                    setQuery("");
                  }}
                  className={`flex w-full items-center gap-2 rounded-xl px-2.5 py-2 text-left text-sm transition hover:bg-[#f7f2ea] dark:hover:bg-white/5 ${
                    m.id === current.id
                      ? "bg-[#fff2ea] text-[#201510] dark:bg-white/10 dark:text-white"
                      : "text-[#7a5b49] dark:text-slate-400"
                  }`}
                >
                  <ModelDot color={m.color} />
                  <span className="flex-1 text-left">{m.name}</span>
                  <span className="flex gap-1">
                    {m.caps?.map((cap) => (
                      <span
                        key={cap}
                        className="rounded-full bg-[#f1e8dc] px-1.5 py-0.5 text-[9px] text-[#7a5b49] dark:bg-white/10 dark:text-slate-300"
                      >
                        {cap}
                      </span>
                    ))}
                  </span>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ModelDot({ color }: { color: string }) {
  return (
    <span
      className="inline-block h-2.5 w-2.5 flex-shrink-0 rounded-full"
      style={{ background: color }}
    />
  );
}
