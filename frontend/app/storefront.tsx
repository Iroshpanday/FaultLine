"use client";

import { useState } from "react";

import { formatPrice, SECTIONS } from "./catalog";
import { openOrderHelp } from "./chat-widget";
import { Steamer } from "./steamer";

const ALL_PRODUCTS = SECTIONS.flatMap((s) => s.products);

const DELIVERY_FACTS = [
  ["Same-day delivery", "in the valley for orders placed before 2 pm"],
  ["Free delivery", "on orders over Rs 2,000"],
  ["Packed at −18 °C", "in insulated boxes that stay cold for six hours"],
];

export function Storefront() {
  const [cart, setCart] = useState<Record<string, number>>({});
  const [justAdded, setJustAdded] = useState<string | null>(null);
  const [cartOpen, setCartOpen] = useState(false);

  const count = Object.values(cart).reduce((a, b) => a + b, 0);
  const total = ALL_PRODUCTS.reduce((sum, p) => sum + (cart[p.id] ?? 0) * p.price, 0);

  function add(id: string) {
    setCart((c) => ({ ...c, [id]: (c[id] ?? 0) + 1 }));
    setJustAdded(id);
    setTimeout(() => setJustAdded((cur) => (cur === id ? null : cur)), 1400);
  }

  return (
    <>
      <p className="bg-pine px-4 py-2 text-center text-sm text-steam/90">
        This is a demo store. Try order help with{" "}
        <span className="font-semibold text-white">demo.customer@example.com</span>
      </p>

      <header className="sticky top-0 z-30 border-b border-line bg-steam/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 sm:px-6">
          <a href="#top" className="flex items-center gap-2.5" aria-label="Momo Mart home">
            <svg viewBox="0 0 32 32" className="size-8" aria-hidden="true">
              <circle cx="16" cy="16" r="15" fill="#d9c9a0" stroke="#b8a370" strokeWidth="2" />
              <circle cx="16" cy="16" r="8" fill="#fbf9f3" stroke="#ddd2b9" strokeWidth="1.5" />
              <circle cx="16" cy="16" r="2.2" fill="#ddd2b9" />
            </svg>
            <span className="font-display text-xl font-extrabold tracking-tight">Momo Mart</span>
          </a>
          <nav className="hidden gap-5 text-sm text-muted md:flex" aria-label="Shop sections">
            {SECTIONS.map((s) => (
              <a key={s.id} href={`#${s.id}`} className="hover:text-pine">
                {s.title}
              </a>
            ))}
          </nav>
          <div className="relative ml-auto">
            <button
              onClick={() => setCartOpen((o) => !o)}
              aria-expanded={cartOpen}
              className="flex items-center gap-2 rounded-full border border-line bg-white px-4 py-2 text-sm font-semibold hover:border-pine-soft"
            >
              Cart
              <span
                className={
                  "grid min-w-6 place-items-center rounded-full px-1.5 text-xs font-bold " +
                  (count ? "bg-turmeric text-pine" : "bg-line text-muted")
                }
              >
                {count}
              </span>
            </button>
            {cartOpen && (
              <div className="absolute right-0 mt-2 w-72 rounded-2xl border border-line bg-white p-4 shadow-[0_18px_40px_-18px_rgba(23,59,52,0.45)]">
                {count === 0 ? (
                  <p className="text-sm text-muted">Your cart is empty. Add something from the menu below.</p>
                ) : (
                  <>
                    <ul className="space-y-2 text-sm">
                      {ALL_PRODUCTS.filter((p) => cart[p.id]).map((p) => (
                        <li key={p.id} className="flex justify-between gap-3">
                          <span>
                            {cart[p.id]} × {p.name}
                          </span>
                          <span className="tabular-nums">{formatPrice(cart[p.id] * p.price)}</span>
                        </li>
                      ))}
                    </ul>
                    <div className="mt-3 flex justify-between border-t border-line pt-3 font-semibold">
                      <span>Total</span>
                      <span className="tabular-nums">{formatPrice(total)}</span>
                    </div>
                    <button
                      disabled
                      className="mt-3 w-full cursor-not-allowed rounded-xl bg-line py-2 text-sm font-semibold text-muted"
                    >
                      Checkout
                    </button>
                    <p className="mt-2 text-xs text-muted">Checkout is switched off in this demo store.</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      <main id="top">
        <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 pt-12 pb-16 sm:px-6 md:grid-cols-[1.1fr_0.9fr] md:pt-20">
          <div>
            <h1 className="font-display text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] font-extrabold tracking-[-0.035em]">
              Momos folded this morning, steaming in your kitchen tonight.
            </h1>
            <p className="mt-6 max-w-[34rem] text-lg leading-relaxed text-muted">
              Frozen momos, small-batch achar and Ilam tea, delivered across Kathmandu, Lalitpur and Bhaktapur in
              insulated boxes.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a href="#momos" className="rounded-full bg-chili px-6 py-3 font-semibold text-white hover:bg-chili-dark">
                Shop frozen momos
              </a>
              <button
                onClick={openOrderHelp}
                className="rounded-full border-2 border-pine px-6 py-3 font-semibold hover:bg-pine hover:text-white"
              >
                Track an order
              </button>
            </div>
          </div>
          <Steamer className="mx-auto w-full max-w-[26rem]" />
        </section>

        <div className="border-y border-line bg-white">
          <ul className="mx-auto grid max-w-6xl divide-line px-4 sm:px-6 md:grid-cols-3 md:divide-x">
            {DELIVERY_FACTS.map(([title, text]) => (
              <li key={title} className="py-5 md:px-6 md:first:pl-0">
                <span className="font-semibold">{title}</span> <span className="text-muted">{text}</span>
              </li>
            ))}
          </ul>
        </div>

        {SECTIONS.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="mx-auto grid max-w-6xl scroll-mt-20 gap-6 px-4 py-14 sm:px-6 md:grid-cols-[16rem_1fr] md:gap-12"
          >
            <div>
              <h2 className="font-display text-3xl font-extrabold tracking-tight">{section.title}</h2>
              <p className="mt-2 text-muted">{section.intro}</p>
            </div>
            <ul className="divide-y divide-line border-y border-line">
              {section.products.map((p) => (
                <li key={p.id} className="flex flex-col gap-3 py-5 sm:flex-row sm:items-center sm:gap-6">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-lg font-bold">{p.name}</h3>
                      {p.tag && (
                        <span className="rounded-full bg-turmeric/30 px-2 py-0.5 text-xs font-semibold text-pine">
                          {p.tag}
                        </span>
                      )}
                    </div>
                    <p className="mt-1 max-w-[38rem] text-muted">{p.description}</p>
                    <p className="mt-1 text-sm text-muted">{p.size}</p>
                  </div>
                  <div className="flex items-center gap-4 sm:flex-col sm:items-end sm:gap-2">
                    <span className="text-lg font-bold text-chili tabular-nums">{formatPrice(p.price)}</span>
                    <button
                      onClick={() => add(p.id)}
                      className={
                        "min-w-28 rounded-full px-4 py-2 text-sm font-semibold transition-colors " +
                        (justAdded === p.id ? "bg-pine text-white" : "border border-pine/30 bg-white hover:border-pine")
                      }
                    >
                      {justAdded === p.id ? "Added" : "Add to cart"}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </main>

      <footer className="mt-10 bg-pine text-steam">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-3">
          <div>
            <p className="font-display text-2xl font-extrabold">Momo Mart</p>
            <p className="mt-2 text-steam/75">Jhamsikhel, Lalitpur. Kitchen open 7 am to 7 pm, every day.</p>
          </div>
          <div>
            <p className="font-semibold">Questions about an order?</p>
            <p className="mt-2 text-steam/75">Open order help in the corner. It checks your order records for you.</p>
          </div>
          <p className="text-sm text-steam/60 md:text-right">
            Momo Mart is a demo store built for Faultline. Products, prices and orders are made up.
          </p>
        </div>
      </footer>
    </>
  );
}
