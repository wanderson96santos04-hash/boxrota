import React from "react";

type InputProps = {
  id?: string;
  inputRef?: React.Ref<HTMLInputElement>;
  placeholder?: string;
  rightHint?: string;
  value?: string;
  onChange?: (v: string) => void;
  onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>;
  onKeyUp?: React.KeyboardEventHandler<HTMLInputElement>;
  onFocus?: React.FocusEventHandler<HTMLInputElement>;
  onBlur?: React.FocusEventHandler<HTMLInputElement>;
  type?: string;
  disabled?: boolean;
  autoFocus?: boolean;
};

export function Input({
  id,
  inputRef,
  placeholder,
  rightHint,
  value,
  onChange,
  onKeyDown,
  onKeyUp,
  onFocus,
  onBlur,
  type = "text",
  disabled = false,
  autoFocus = false,
}: InputProps) {
  return (
    <div className="relative">
      <input
        id={id}
        ref={inputRef}
        type={type}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onKeyDown={onKeyDown}
        onKeyUp={onKeyUp}
        onFocus={onFocus}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autoFocus}
        className="h-12 w-full rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 pr-14 text-sm text-[var(--title)] placeholder:text-[var(--muted)] outline-none focus:border-[color:rgba(47,107,255,0.55)] focus:ring-2 focus:ring-[color:rgba(47,107,255,0.18)] disabled:opacity-60"
      />
      {rightHint ? (
        <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded-xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-2 py-1 text-[10px] font-medium text-[var(--muted)]">
          {rightHint}
        </div>
      ) : null}
    </div>
  );
}