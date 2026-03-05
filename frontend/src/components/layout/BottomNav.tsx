import { NavLink } from "react-router-dom";

const items = [
  { to: "/app", label: "Início" },
  { to: "/app/services", label: "OS" },
  { to: "/app/customers", label: "Clientes" },
  { to: "/app/parts", label: "Peças" },
  { to: "/app/marketplace", label: "Market" },
];

function cls(isActive: boolean) {
  return [
    "flex flex-1 flex-col items-center justify-center gap-1 rounded-2xl px-2 py-2 transition",
    isActive
      ? "bg-[color:rgba(47,107,255,0.16)] text-[var(--title)]"
      : "text-[var(--muted)] hover:bg-[color:rgba(255,255,255,0.04)] hover:text-[var(--title)]",
  ].join(" ");
}

export default function BottomNav() {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-[var(--border)] bg-[color:rgba(17,26,46,0.92)] backdrop-blur">
      <div className="mx-auto max-w-[520px] px-3 py-3">
        <div className="flex gap-2">
          {items.map((i) => (
            <NavLink key={i.to} to={i.to} end={i.to === "/app"}>
              {({ isActive }) => (
                <div className={cls(isActive)}>
                  <div className="h-1.5 w-1.5 rounded-full bg-current opacity-70" />
                  <div className="text-[11px] font-medium leading-none">
                    {i.label}
                  </div>
                </div>
              )}
            </NavLink>
          ))}
        </div>
      </div>
    </div>
  );
}