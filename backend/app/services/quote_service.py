import re
import secrets
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppException
from app.models.customer import Customer, Vehicle
from app.models.quote import Quote
from app.models.service import Service, ServiceItem
from app.models.user import User


_ALLOWED_STATUSES = {"draft", "sent", "approved", "rejected"}


def _q2(v: Decimal) -> Decimal:
    return (v or Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _money_str(v: Decimal) -> str:
    return f"{_q2(v):.2f}"


def _advisory_lock_for_workshop(db: Session, workshop_id: uuid.UUID) -> None:
    # trava por transação para gerar sequencial sem corrida
    key = int(workshop_id.int % 2147483647)
    db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": key})


def _next_quote_number(db: Session, workshop_id: uuid.UUID) -> str:
    _advisory_lock_for_workshop(db, workshop_id)

    last = (
        db.query(Quote.quote_number)
        .filter(Quote.workshop_id == workshop_id)
        .order_by(Quote.created_at.desc())
        .limit(1)
        .scalar()
    )

    n = 0
    if last:
        m = re.search(r"(\d+)$", str(last))
        if m:
            try:
                n = int(m.group(1))
            except ValueError:
                n = 0

    n += 1
    return f"QUO-{n:06d}"


def _public_token() -> str:
    # ~43-50 chars, safe for URL
    return secrets.token_urlsafe(32)[:64]


def _load_service(db: Session, *, user: User, service_id: uuid.UUID) -> Service:
    s = (
        db.query(Service)
        .options(
            joinedload(Service.vehicle),
            joinedload(Service.customer),
            joinedload(Service.items),
        )
        .filter(Service.workshop_id == user.workshop_id, Service.id == service_id)
        .one_or_none()
    )
    if not s:
        raise AppException(404, "not_found", "Serviço não encontrado.")
    return s


def _recalc_service_totals(db: Session, service: Service) -> tuple[Decimal, Decimal]:
    subtotal = (
        db.query(func.coalesce(func.sum(ServiceItem.total_price), 0))
        .filter(ServiceItem.service_id == service.id, ServiceItem.workshop_id == service.workshop_id)
        .scalar()
    )
    subtotal_d = _q2(Decimal(subtotal or 0))
    total_d = _q2(subtotal_d + _q2(Decimal(service.labor_amount or 0)))
    return subtotal_d, total_d


def _snapshot_from_service(db: Session, service: Service) -> dict[str, Any]:
    vehicle: Vehicle | None = getattr(service, "vehicle", None)
    customer: Customer | None = getattr(service, "customer", None)

    subtotal_d, total_d = _recalc_service_totals(db, service)

    items = []
    for it in (service.items or []):
        items.append(
            {
                "id": str(it.id),
                "description": it.description,
                "qty": int(it.qty or 0),
                "unit_price": _money_str(Decimal(it.unit_price or 0)),
                "total_price": _money_str(Decimal(it.total_price or 0)),
                "part_id": str(it.part_id) if it.part_id else None,
            }
        )

    return {
        "service": {
            "id": str(service.id),
            "status": service.status,
            "notes": service.notes,
            "created_at": service.created_at.isoformat() if service.created_at else None,
            "updated_at": service.updated_at.isoformat() if service.updated_at else None,
        },
        "vehicle": {
            "id": str(vehicle.id) if vehicle else None,
            "plate": (vehicle.plate if vehicle else "") or "",
        },
        "customer": {
            "id": str(customer.id) if customer else None,
            "name": (customer.name if customer else None),
            "phone": (customer.phone if customer else None),
        },
        "items": items,
        "labor_amount": _money_str(Decimal(service.labor_amount or 0)),
        "subtotal_amount": _money_str(subtotal_d),
        "total_amount": _money_str(total_d),
    }


def get_quote(db: Session, *, user: User, quote_id: uuid.UUID) -> Quote:
    q = (
        db.query(Quote)
        .filter(Quote.workshop_id == user.workshop_id, Quote.id == quote_id)
        .one_or_none()
    )
    if not q:
        raise AppException(404, "not_found", "Orçamento não encontrado.")
    return q


def get_quote_by_token(db: Session, *, token: str) -> Quote:
    tok = (token or "").strip()
    if not tok:
        raise AppException(404, "not_found", "Orçamento não encontrado.")
    q = db.query(Quote).filter(Quote.public_token == tok).one_or_none()
    if not q:
        raise AppException(404, "not_found", "Orçamento não encontrado.")
    return q


def create_from_service(db: Session, *, user: User, service_id: uuid.UUID) -> Quote:
    service = _load_service(db, user=user, service_id=service_id)

    existing = (
        db.query(Quote)
        .filter(Quote.workshop_id == user.workshop_id, Quote.service_id == service.id)
        .order_by(Quote.created_at.desc())
        .first()
    )
    if existing:
        return existing

    qn = _next_quote_number(db, user.workshop_id)
    token = _public_token()

    snap = _snapshot_from_service(db, service)
    subtotal = Decimal(snap.get("subtotal_amount") or "0")
    total = Decimal(snap.get("total_amount") or "0")

    q = Quote(
        workshop_id=user.workshop_id,
        service_id=service.id,
        quote_number=qn,
        status="draft",
        public_token=token,
        snapshot=snap,
        html_cache=None,
        subtotal_amount=_q2(subtotal),
        total_amount=_q2(total),
    )
    db.add(q)
    db.flush()
    db.refresh(q)
    return q


def update_status(db: Session, *, user: User, quote_id: uuid.UUID, status: str) -> Quote:
    q = get_quote(db, user=user, quote_id=quote_id)
    st = (status or "").strip().lower()
    if st not in _ALLOWED_STATUSES:
        raise AppException(400, "invalid_status", "Status inválido.")
    q.status = st
    db.add(q)
    db.flush()
    db.refresh(q)
    return q


def render_quote_html(db: Session, *, quote: Quote, public_url: str) -> str:
    snap = quote.snapshot or {}
    vehicle = (snap.get("vehicle") or {}) if isinstance(snap, dict) else {}
    customer = (snap.get("customer") or {}) if isinstance(snap, dict) else {}
    items = (snap.get("items") or []) if isinstance(snap, dict) else []
    labor = str(snap.get("labor_amount") or "0.00")
    subtotal = str(snap.get("subtotal_amount") or "0.00")
    total = str(snap.get("total_amount") or "0.00")

    plate = (vehicle.get("plate") or "").upper()
    cname = customer.get("name") or ""
    cphone = customer.get("phone") or ""
    status = (quote.status or "draft").upper()

    def brl(v: str) -> str:
        try:
            d = Decimal(str(v or "0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            s = f"{d:.2f}"
            a, b = s.split(".")
            a = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1.", a)
            return f"R$ {a},{b}"
        except Exception:
            return f"R$ {v}"

    rows_html = ""
    for it in items:
        desc = str((it or {}).get("description") or "")[:160]
        qty = int((it or {}).get("qty") or 0)
        up = brl(str((it or {}).get("unit_price") or "0.00"))
        tp = brl(str((it or {}).get("total_price") or "0.00"))
        rows_html += f"""
          <div class="row">
            <div class="desc">{desc}</div>
            <div class="qty">{qty}x</div>
            <div class="unit">{up}</div>
            <div class="total">{tp}</div>
          </div>
        """

    if not rows_html:
        rows_html = """
          <div class="empty">
            Nenhum item lançado ainda. Se algo ficou de fora, responda pedindo ajuste.
          </div>
        """

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{quote.quote_number} • BoxRota</title>
  <style>
    :root {{
      --bg:#0B1020; --surface:#111A2E; --border:#1E2A46;
      --primary:#2F6BFF; --primaryHover:#2356D6;
      --title:#F4F7FF; --text:#C9D3EF; --muted:#8FA3D6;
      --success:#20C997; --danger:#FF4D4D; --warning:#FFB020;
      --r:14px;
    }}
    *{{box-sizing:border-box}}
    body{{margin:0;background:linear-gradient(180deg,rgba(47,107,255,.10),transparent 35%),var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial}}
    .wrap{{max-width:920px;margin:0 auto;padding:20px}}
    .card{{background:rgba(17,26,46,.92);border:1px solid var(--border);border-radius:20px;box-shadow:0 12px 30px rgba(0,0,0,.25);overflow:hidden}}
    .top{{padding:18px 18px 10px;border-bottom:1px solid var(--border);display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap}}
    .brand{{display:flex;gap:10px;align-items:center}}
    .logo{{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,var(--primary),#74a2ff);box-shadow:0 10px 30px rgba(47,107,255,.25)}}
    .brand h1{{margin:0;font-size:14px;color:var(--title);letter-spacing:.2px}}
    .pill{{font-size:12px;padding:6px 10px;border-radius:999px;border:1px solid var(--border);background:rgba(255,255,255,.03);color:var(--muted)}}
    .head{{padding:16px 18px;display:grid;gap:14px;grid-template-columns:1.2fr .8fr}}
    @media (max-width:720px){{.head{{grid-template-columns:1fr}}}}
    .hTitle{{font-size:20px;color:var(--title);margin:0}}
    .sub{{font-size:13px;color:var(--muted);margin-top:6px;line-height:1.35}}
    .kv{{display:grid;gap:8px}}
    .kv .line{{display:flex;gap:10px;justify-content:space-between;border:1px solid var(--border);border-radius:14px;padding:10px 12px;background:rgba(255,255,255,.02)}}
    .k{{color:var(--muted);font-size:12px}}
    .v{{color:var(--title);font-size:12px;text-align:right;max-width:62%}}
    .items{{padding:0 18px 14px}}
    .gridHead{{display:grid;grid-template-columns:1fr 72px 110px 110px;gap:10px;font-size:12px;color:var(--muted);padding:10px 12px;border:1px solid var(--border);border-radius:14px;background:rgba(255,255,255,.02)}}
    .row{{display:grid;grid-template-columns:1fr 72px 110px 110px;gap:10px;padding:10px 12px;border-bottom:1px solid rgba(30,42,70,.7)}}
    .row .desc{{color:var(--title);font-size:13px}}
    .row .qty,.row .unit,.row .total{{font-size:13px;text-align:right}}
    .empty{{padding:14px 12px;color:var(--muted);font-size:13px}}
    .totals{{padding:14px 18px 18px;border-top:1px solid var(--border);display:grid;grid-template-columns:1fr .8fr;gap:14px;align-items:start}}
    @media (max-width:720px){{.totals{{grid-template-columns:1fr}}}}
    .big{{border:1px solid var(--border);border-radius:18px;background:rgba(255,255,255,.02);padding:12px}}
    .big .label{{font-size:12px;color:var(--muted)}}
    .big .value{{font-size:34px;font-weight:800;letter-spacing:.2px;color:var(--title);margin-top:6px}}
    .mini{{display:grid;gap:10px}}
    .mini .line{{display:flex;justify-content:space-between;gap:10px;border:1px solid var(--border);border-radius:14px;padding:10px 12px;background:rgba(255,255,255,.02)}}
    .btns{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}}
    .btn{{appearance:none;border:0;cursor:pointer;border-radius:14px;padding:12px 14px;font-weight:800;font-size:13px}}
    .btn.primary{{background:var(--primary);color:#fff}}
    .btn.primary:hover{{background:var(--primaryHover)}}
    .btn.ghost{{background:rgba(255,255,255,.03);color:var(--title);border:1px solid var(--border)}}
    .foot{{padding:14px 18px;color:var(--muted);font-size:12px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}}
    a{{color:inherit}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="top">
        <div class="brand">
          <div class="logo"></div>
          <div>
            <h1>BoxRota</h1>
            <div class="pill">Orçamento {quote.quote_number} • {status}</div>
          </div>
        </div>
        <div class="pill">Abrir no celular e aprovar em 1 toque</div>
      </div>

      <div class="head">
        <div>
          <p class="hTitle">Orçamento claro. Sem surpresa na entrega.</p>
          <p class="sub">
            Placa <b style="color:var(--title)">{plate or "-"}</b>.
            {(" Cliente " + cname) if cname else " Cliente não informado."}
            {(" • " + cphone) if cphone else ""}
          </p>
          <div class="btns">
            <button class="btn ghost" onclick="window.print()">Imprimir</button>
            <a class="btn primary" href="{public_url}" target="_blank" rel="noreferrer">Abrir link</a>
          </div>
        </div>

        <div class="kv">
          <div class="line"><div class="k">Placa</div><div class="v">{plate or "-"}</div></div>
          <div class="line"><div class="k">Cliente</div><div class="v">{cname or "-"}</div></div>
          <div class="line"><div class="k">WhatsApp</div><div class="v">{cphone or "-"}</div></div>
          <div class="line"><div class="k">Número</div><div class="v">{quote.quote_number}</div></div>
        </div>
      </div>

      <div class="items">
        <div class="gridHead">
          <div>Item</div><div style="text-align:right">Qtd</div><div style="text-align:right">Unit</div><div style="text-align:right">Total</div>
        </div>
        {rows_html}
      </div>

      <div class="totals">
        <div class="big">
          <div class="label">TOTAL</div>
          <div class="value">{brl(total)}</div>
          <div class="btns" style="margin-top:14px">
            <a class="btn primary" href="#" onclick="openWhatsApp();return false;">WhatsApp</a>
            <button class="btn ghost" onclick="window.print()">Imprimir</button>
          </div>
        </div>
        <div class="mini">
          <div class="line"><div class="k">Subtotal</div><div class="v">{brl(subtotal)}</div></div>
          <div class="line"><div class="k">Mão de obra</div><div class="v">{brl(labor)}</div></div>
          <div class="line"><div class="k">Status</div><div class="v">{status}</div></div>
        </div>
      </div>

      <div class="foot">
        <div>Gerado pelo BoxRota • “Retorno automático. Oficina organizada.”</div>
        <div>Link público: <a href="{public_url}">{quote.public_token}</a></div>
      </div>
    </div>
  </div>

  <script>
    function openWhatsApp() {{
      const phone = "{cphone}".replace(/\\D/g,'');
      const plate = "{plate}".replace(/[^A-Z0-9]/g,'');
      const total = "{brl(total)}";
      const msg =
        "Olá! Sobre o orçamento {quote.quote_number} do veículo " + (plate || "-") +
        "\\nTotal: " + total +
        "\\n\\nVocê aprova esse orçamento? (Responda: APROVAR ou REJEITAR)";
      if (!phone) {{
        alert("Telefone do cliente não informado.");
        return;
      }}
      const url = "https://wa.me/55" + phone + "?text=" + encodeURIComponent(msg);
      window.open(url, "_blank");
    }}
  </script>
</body>
</html>
"""
    return html


def get_or_build_html(db: Session, *, user: User, quote_id: uuid.UUID, app_public_base: str) -> str:
    q = get_quote(db, user=user, quote_id=quote_id)
    public_url = f"{app_public_base.rstrip('/')}/public/q/{q.public_token}"
    if q.html_cache and str(q.html_cache).strip():
        return q.html_cache
    html = render_quote_html(db, quote=q, public_url=public_url)
    q.html_cache = html
    db.add(q)
    db.flush()
    db.refresh(q)
    return html


def get_public_html(db: Session, *, token: str, app_public_base: str) -> str:
    q = get_quote_by_token(db, token=token)
    public_url = f"{app_public_base.rstrip('/')}/public/q/{q.public_token}"
    if q.html_cache and str(q.html_cache).strip():
        return q.html_cache
    html = render_quote_html(db, quote=q, public_url=public_url)
    q.html_cache = html
    db.add(q)
    db.flush()
    db.refresh(q)
    return html