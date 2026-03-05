import React from "react";

export function Input({
  placeholder,
  rightHint,
  value,
  onChange,
}: {
  placeholder?: string;
  rightHint?: string;
  value?: string;
  onChange?: (v: string) => void;
}) {
  return (
    <div className="relative">
      <input
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className="h-12 w-full rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 pr-14 text-sm text-[var(--title)] placeholder:text-[var(--muted)] outline-none focus:border-[color:rgba(47,107,255,0.55)] focus:ring-2 focus:ring-[color:rgba(47,107,255,0.18)]"
      />
      {rightHint ? (
        <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded-xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-2 py-1 text-[10px] font-medium text-[var(--muted)]">
          {rightHint}
        </div>
      ) : null}
    </div>
  );
}