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

/** Opens the chat from anywhere on the page. */
export function openOrderHelp() {
  window.dispatchEvent(new Event(OPEN_EVENT));
}

/** The nav's "Order help" word: a button, because it opens the chat rather than going somewhere. */
export function OrderHelpButton({ className, label = "Order help" }: { className?: string; label?: string }) {
  return (
    <button type="button" className={className} onClick={openOrderHelp}>
      {label}
    </button>
  );
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
  const log = useRef<HTMLDivElement>(null);

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
    if (open) firstField.current?.focus({ preventScroll: true });
  }, [open, email]);

  // Keep the newest message in view, scrolling only the chat, never the page.
  useEffect(() => {
    const el = log.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [bubbles, sending]);

  const close = useCallback(() => {
    setOpen(false);
    launcher.current?.focus({ preventScroll: true });
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
    <div className="oh">
      {open && (
        <div role="dialog" aria-label="Order help" className="oh-panel">
          <div className="oh-head">
            <div>
              <p className="oh-title">Order help</p>
              <p className="oh-sub">Checks your Momo Mart orders and answers in a few seconds</p>
            </div>
            <button onClick={close} aria-label="Close order help" className="oh-icon-btn">
              <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true">
                <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
          </div>

          {!email ? (
            <form onSubmit={startChat} className="oh-gate">
              <p>Enter the email you used at checkout. Order help only shows orders placed with it.</p>
              <label className="oh-field">
                <span>Email</span>
                <input
                  ref={firstField}
                  type="email"
                  required
                  autoComplete="email"
                  value={emailDraft}
                  onChange={(e) => setEmailDraft(e.target.value)}
                  placeholder="you@example.com"
                />
              </label>
              <button type="submit" className="oh-primary">
                Start chat
              </button>
              <div className="oh-demo">
                <p>
                  Trying the demo? Use <strong>{DEMO_EMAIL}</strong>, which has orders #123 to #126.
                </p>
                <button type="button" onClick={() => setEmailDraft(DEMO_EMAIL)} className="oh-text-btn">
                  Use the demo email
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="oh-who">
                <span>Orders for {email}</span>
                <button onClick={changeEmail} className="oh-text-btn">
                  Change
                </button>
              </div>

              <div ref={log} className="oh-log" aria-live="polite">
                <div className="oh-msg oh-msg--assistant">
                  Hi! Ask me about any of your orders: where it is, or when it was delivered.
                </div>

                {bubbles.length === 0 && (
                  <div className="oh-chips">
                    {SUGGESTIONS.map((q) => (
                      <button key={q} onClick={() => send(q)} className="oh-chip">
                        {q}
                      </button>
                    ))}
                  </div>
                )}

                {bubbles.map((b, i) => (
                  <div key={i} className={`oh-msg oh-msg--${b.role}`}>
                    {renderText(b.text)}
                    {b.retry && i === bubbles.length - 1 && (
                      <button
                        onClick={() => send(b.retry!, bubbles.slice(0, -2))}
                        disabled={sending}
                        className="oh-text-btn oh-retry"
                      >
                        Try again
                      </button>
                    )}
                  </div>
                ))}

                {sending && (
                  <div className="oh-msg oh-msg--assistant oh-typing" aria-label="Order help is checking">
                    <span />
                    <span />
                    <span />
                  </div>
                )}
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send(input);
                }}
                className="oh-compose"
              >
                <input
                  ref={firstField}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  maxLength={1000}
                  placeholder="Ask about an order"
                  aria-label="Your message"
                />
                <button type="submit" disabled={sending || !input.trim()} aria-label="Send" className="oh-send">
                  <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true">
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
        className={"oh-launcher" + (open ? " is-open" : "")}
      >
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
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
    </div>
  );
}
