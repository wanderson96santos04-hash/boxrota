import React from "react";

export function Card({
  title,
  subtitle,
  right,
  children,
}: {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
  children?: React.ReactNode;
}) {
  return (
    <div className="rounded-[14px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_10px_30px_rgba(0,0,0,0.22)]">
      <div className="flex items-start justify-between gap-3 px-5 pt-5">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-[var(--title)]">
            {title}
          </div>
          {subtitle ? (
            <div className="mt-1 text-xs text-[var(--muted)]">{subtitle}</div>
          ) : null}
        </div>
        {right ? <div className="shrink-0">{right}</div> : null}
      </div>
      <div className="px-5 pb-5 pt-4">{children}</div>
    </div>
  );
}