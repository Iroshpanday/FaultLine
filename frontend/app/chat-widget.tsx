"use client";

import { FormEvent, ReactNode, useCallback, useEffect, useRef, useState } from "react";

const STORE_SLUG = "momo-mart";
const DEMO_EMAIL = "demo.customer@example.com";
const OPEN_EVENT = "momo-mart:open-order-help";
const EMAIL_KEY = "momo-mart:order-help-email";
const SUGGESTIONS = ["Where is my order #123?", "Has order #125 been delivered?", "What's happening with #124?"];

type Bubble = {
  role: "user" | "assistant" | "error";
  text: string;
  retry?: string; // the message to resend when the error has a retry button
};

/** Lets any button on the page open the chat ("Track an order" in the hero). */
export function openOrderHelp() {
  window.dispatchEvent(new Event(OPEN_EVENT));
}

function readSavedEmail(): string {
  try {
    return sessionStorage.getItem(EMAIL_KEY) ?? "";
  } catch {
    return "";
  }
}

function saveEmail(email: string) {
  try {
    if (email) sessionStorage.setItem(EMAIL_KEY, email);
    else sessionStorage.removeItem(EMAIL_KEY);
  } catch {
    // private mode: the chat still works, it just forgets the email on reload
  }
}

// Outside the component: one request to our API, turned into a chat bubble.
async function askAgent(message: string, email: string, history: Bubble[]): Promise<Bubble> {
  try {
    const resp = await fetch(`/api/stores/${STORE_SLUG}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // New key per message: a network retry of this exact request gets a
        // 409 instead of a second (paid) answer.
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify({
        message,
        email,
        // Earlier turns so follow-ups like "and #125?" make sense.
        history: history
          .filter((b) => b.role !== "error")
          .slice(-10)
          .map((b) => ({ role: b.role, content: b.text })),
      }),
    });
    const data = await resp.json().catch(() => ({}));
    if (resp.ok) return { role: "assistant", text: data.answer };
    if (resp.status === 429) {
      return { role: "error", text: "You've sent a lot of messages in a short time. Wait a minute, then try again." };
    }
    if (resp.status >= 500) {
      // 503: the AI provider failed. 500/502/504: our server is down or restarting.
      return { role: "error", text: "Order help couldn't answer just now.", retry: message };
    }
    return { role: "error", text: `That didn't go through (error ${resp.status}).`, retry: message };
  } catch {
    return { role: "error", text: "Can't reach Momo Mart right now. Check your connection.", retry: message };
  }
}

// Models sometimes answer with **bold** even when asked not to. Render that,
// and nothing else, without ever injecting HTML.
function renderText(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong> : part,
  );
}

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [emailDraft, setEmailDraft] = useState("");
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const launcher = useRef<HTMLButtonElement>(null);
  const firstField = useRef<HTMLInputElement>(null);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = readSavedEmail();
    // One-time restore on load: the saved email, and /#order-help opens the
    // chat straight away (handy for sharing a link to the demo).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (saved) setEmail(saved);
    if (window.location.hash === "#order-help") setOpen(true);
  }, []);

  useEffect(() => {
    const onOpen = () => setOpen(true);
    window.addEventListener(OPEN_EVENT, onOpen);
    return () => window.removeEventListener(OPEN_EVENT, onOpen);
  }, []);

  useEffect(() => {
    if (open) firstField.current?.focus();
  }, [open, email]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [bubbles, sending]);

  const close = useCallback(() => {
    setOpen(false);
    launcher.current?.focus();
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && close();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close]);

  function startChat(e: FormEvent) {
    e.preventDefault();
    const value = emailDraft.trim();
    if (!value) return;
    setEmail(value);
    saveEmail(value);
  }

  function changeEmail() {
    setEmail("");
    setEmailDraft("");
    setBubbles([]);
    saveEmail("");
  }

  // `earlier` = the conversation before this message. A retry passes the
  // conversation minus the failed message and its error bubble.
  async function send(text: string, earlier: Bubble[] = bubbles) {
    const message = text.trim();
    if (!message || sending) return;
    setInput("");
    setSending(true);
    setBubbles([...earlier, { role: "user", text: message }]);
    const reply = await askAgent(message, email, earlier);
    setBubbles((b) => [...b, reply]);
    setSending(false);
  }

  return (
    <>
      {open && (
        <div
          role="dialog"
          aria-label="Order help"
          className="panel-in fixed inset-0 z-50 flex flex-col overflow-hidden bg-white sm:inset-auto sm:right-6 sm:bottom-24 sm:h-[min(36rem,calc(100dvh-8rem))] sm:w-94 sm:rounded-3xl sm:border sm:border-line sm:shadow-[0_30px_70px_-30px_rgba(23,59,52,0.6)]"
        >
          <div className="flex items-start gap-3 bg-pine px-5 py-4 text-white">
            <div className="flex-1">
              <p className="font-display text-lg font-bold">Order help</p>
              <p className="text-sm text-white/75">An AI assistant that checks your Momo Mart orders</p>
            </div>
            <button
              onClick={close}
              aria-label="Close order help"
              className="-mr-1 grid size-9 place-items-center rounded-full hover:bg-white/10"
            >
              <svg viewBox="0 0 20 20" className="size-5" aria-hidden="true">
                <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
          </div>

          {!email ? (
            <form onSubmit={startChat} className="flex flex-1 flex-col gap-4 p-5">
              <p className="text-pine">
                Enter the email you used at checkout. Order help only shows orders placed with that email.
              </p>
              <label className="flex flex-col gap-1.5 text-sm font-semibold">
                Email
                <input
                  ref={firstField}
                  type="email"
                  required
                  autoComplete="email"
                  value={emailDraft}
                  onChange={(e) => setEmailDraft(e.target.value)}
                  placeholder="you@example.com"
                  className="rounded-xl border border-line px-4 py-2.5 text-base font-normal outline-none focus:border-pine"
                />
              </label>
              <button type="submit" className="rounded-xl bg-chili py-2.5 font-semibold text-white hover:bg-chili-dark">
                Start chat
              </button>
              <div className="mt-auto rounded-2xl bg-steam p-4 text-sm text-muted">
                Trying the demo? Use <span className="font-semibold text-pine">{DEMO_EMAIL}</span>. It has orders
                #123 to #126.
                <button
                  type="button"
                  onClick={() => setEmailDraft(DEMO_EMAIL)}
                  className="mt-2 block font-semibold text-chili underline-offset-2 hover:underline"
                >
                  Use the demo email
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="flex items-center justify-between border-b border-line px-5 py-2 text-xs text-muted">
                <span className="truncate">Orders for {email}</span>
                <button onClick={changeEmail} className="ml-3 shrink-0 font-semibold text-pine hover:underline">
                  Change
                </button>
              </div>

              <div className="flex-1 space-y-3 overflow-y-auto bg-steam/60 px-4 py-4" aria-live="polite">
                <div className="max-w-[85%] rounded-2xl rounded-bl-md border border-line bg-white px-4 py-2.5 text-[0.95rem]">
                  Hi! Ask me about any of your orders, for example where it is or when it was delivered.
                </div>

                {bubbles.length === 0 && (
                  <div className="flex flex-wrap gap-2 pt-1">
                    {SUGGESTIONS.map((q) => (
                      <button
                        key={q}
                        onClick={() => send(q)}
                        className="rounded-full border border-pine/25 bg-white px-3 py-1.5 text-sm hover:border-pine"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}

                {bubbles.map((b, i) => (
                  <div key={i} className={b.role === "user" ? "flex justify-end" : "flex justify-start"}>
                    <div
                      className={
                        "max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-[0.95rem] " +
                        (b.role === "user"
                          ? "rounded-br-md bg-pine text-white"
                          : b.role === "error"
                            ? "rounded-bl-md border border-chili/30 bg-chili/5 text-chili-dark"
                            : "rounded-bl-md border border-line bg-white")
                      }
                    >
                      {renderText(b.text)}
                      {b.retry && i === bubbles.length - 1 && (
                        <button
                          onClick={() => send(b.retry!, bubbles.slice(0, -2))}
                          disabled={sending}
                          className="mt-1.5 block font-semibold underline-offset-2 hover:underline"
                        >
                          Try again
                        </button>
                      )}
                    </div>
                  </div>
                ))}

                {sending && (
                  <div className="flex justify-start" aria-label="Order help is checking">
                    <div className="typing flex gap-1 rounded-2xl rounded-bl-md border border-line bg-white px-4 py-3.5">
                      <span className="size-1.5 rounded-full bg-pine" />
                      <span className="size-1.5 rounded-full bg-pine" />
                      <span className="size-1.5 rounded-full bg-pine" />
                    </div>
                  </div>
                )}
                <div ref={bottom} />
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send(input);
                }}
                className="flex gap-2 border-t border-line bg-white p-3"
              >
                <input
                  ref={firstField}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  maxLength={1000}
                  placeholder="Ask about an order"
                  aria-label="Your message"
                  className="min-w-0 flex-1 rounded-xl border border-line px-4 py-2.5 outline-none focus:border-pine"
                />
                <button
                  type="submit"
                  disabled={sending || !input.trim()}
                  aria-label="Send"
                  className="grid size-11 shrink-0 place-items-center rounded-xl bg-chili text-white hover:bg-chili-dark disabled:opacity-40"
                >
                  <svg viewBox="0 0 20 20" className="size-5" aria-hidden="true">
                    <path d="M3 10l14-6-6 14-2-6-6-2z" fill="currentColor" />
                  </svg>
                </button>
              </form>
            </>
          )}
        </div>
      )}

      <button
        ref={launcher}
        onClick={() => (open ? close() : setOpen(true))}
        aria-expanded={open}
        className={
          "fixed right-4 bottom-4 z-40 flex items-center gap-2 rounded-full bg-pine py-3 pr-5 pl-4 font-semibold text-white shadow-[0_14px_30px_-12px_rgba(23,59,52,0.7)] hover:bg-pine-soft sm:right-6 sm:bottom-6 " +
          (open ? "max-sm:hidden" : "")
        }
      >
        <svg viewBox="0 0 24 24" className="size-5" aria-hidden="true">
          {open ? (
            <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          ) : (
            <path
              d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 4v-4h0A1.5 1.5 0 0 1 4 14.5z"
              fill="currentColor"
            />
          )}
        </svg>
        {open ? "Close" : "Order help"}
      </button>
    </>
  );
}
