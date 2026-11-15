"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type Message = {
  role: "customer" | "assistant" | "error";
  text: string;
  seconds?: number; // how long the answer took (E11: people won't wait 12 s)
};

const EXAMPLES = ["Where is my order #123?", "Where is my order #124?", "Where is my order #999?"];

// Plain function, outside the component: one request to our API, turned
// into a chat bubble. Status codes map 1:1 to what the Django view returns.
async function askAgent(storeSlug: string, message: string): Promise<Message> {
  const started = performance.now();
  try {
    const resp = await fetch(`/api/stores/${storeSlug}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // New key per message. If this exact request is sent twice
        // (network retry), the server answers 409 instead of paying twice.
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify({ message }),
    });
    const data = await resp.json().catch(() => ({}));
    const seconds = (performance.now() - started) / 1000;

    if (resp.ok) return { role: "assistant", text: data.answer, seconds };
    if (resp.status === 429) return { role: "error", text: "Too many messages. Please wait a minute." };
    return { role: "error", text: data.error ?? `Something went wrong (HTTP ${resp.status}).` };
  } catch {
    return { role: "error", text: "Can't reach the server. Is Django running on port 8000?" };
  }
}

export function Chat({ storeSlug, storeName }: { storeSlug: string; storeName: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function send(text: string) {
    const message = text.trim();
    if (!message || sending) return; // ignore double-clicks while waiting
    setInput("");
    setSending(true);
    setMessages((m) => [...m, { role: "customer", text: message }]);

    const reply = await askAgent(storeSlug, message);
    setMessages((m) => [...m, reply]);
    setSending(false);
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    send(input);
  }

  return (
    <div className="mx-auto flex h-dvh w-full max-w-2xl flex-col px-4">
      <header className="border-b border-zinc-200 py-4 dark:border-zinc-800">
        <h1 className="text-lg font-semibold">{storeName} support</h1>
        <p className="text-sm text-zinc-500">Ask about your order. Demo data only.</p>
      </header>

      <main className="flex-1 space-y-3 overflow-y-auto py-4">
        {messages.length === 0 && (
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="rounded-full border border-zinc-300 px-3 py-1.5 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={m.role === "customer" ? "flex justify-end" : "flex justify-start"}>
            <div
              className={
                "max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm " +
                (m.role === "customer"
                  ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                  : m.role === "error"
                    ? "bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200"
                    : "bg-zinc-100 dark:bg-zinc-900")
              }
            >
              {m.text}
              {m.seconds !== undefined && (
                <div className="mt-1 text-xs text-zinc-500">answered in {m.seconds.toFixed(1)} s</div>
              )}
            </div>
          </div>
        ))}

        {sending && <div className="text-sm text-zinc-500">Assistant is checking…</div>}
        <div ref={bottom} />
      </main>

      <form onSubmit={onSubmit} className="flex gap-2 border-t border-zinc-200 py-4 dark:border-zinc-800">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          maxLength={1000}
          placeholder="Where is my order #123?"
          aria-label="Your message"
          className="flex-1 rounded-xl border border-zinc-300 bg-transparent px-4 py-2 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-xl bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
        >
          Send
        </button>
      </form>
    </div>
  );
}
