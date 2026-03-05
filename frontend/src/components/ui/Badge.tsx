import React from "react";

type Tone = "primary" | "success" | "warning" | "danger" | "neutral";

const toneCls: Record<Tone, string> = {
  primary:
    "bg-[color:rgba(47,107,255,0.18)] text-[var(--title)] ring-[color:rgba(47,107,255,0.30)]",
  success:
    "bg-[color:rgba(32,201,151,0.16)] text-[var(--title)] ring-[color:rgba(32,201,151,0.28)]",
  warning:
    "bg-[color:rgba(255,176,32,0.16)] text-[var(--title)] ring-[color:rgba(255,176,32,0.28)]",
  danger:
    "bg-[color:rgba(255,77,77,0.14)] text-[var(--title)] ring-[color:rgba(255,77,77,0.24)]",
  neutral:
    "bg-[color:rgba(255,255,255,0.06)] text-[var(--text)] ring-[var(--border)]",
};

export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: Tone;
}) {
  return (
    <span
      className={[
        "inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1",
        toneCls[tone],
      ].join(" ")}
    >
      {children}
    </span>
  );
}