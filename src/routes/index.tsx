import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import hound from "@/assets/dog-sri-lankan-hound.jpg";
import golden from "@/assets/dog-golden-retriever.jpg";
import collie from "@/assets/dog-border-collie.jpg";
import pointer from "@/assets/dog-malay-pointer.jpg";
import indie from "@/assets/dog-indie.jpg";
import labrador from "@/assets/dog-labrador.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Know Your Dog — Friendly Vet Chat for Dog Health" },
      {
        name: "description",
        content:
          "Ask a friendly vet copilot about your dog's symptoms. Pick breed, age and weight for guidance tailored to your dog.",
      },
      { property: "og:title", content: "Know Your Dog — Friendly Vet Chat" },
      {
        property: "og:description",
        content:
          "Chat about vomiting, lethargy, skin rashes and more, with guidance tuned to your dog's breed, age and weight.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

type Message = { role: "user" | "assistant"; content: string };

const BREEDS = [
  "Srilankan Hound",
  "Malay Pointer",
  "Indie Native Dog",
  "Golden Retriever",
  "Labrador Retriever",
  "Border Collie",
];

const SYMPTOMS = [
  { emoji: "🤮", label: "Vomiting" },
  { emoji: "😴", label: "Lethargy" },
  { emoji: "🩹", label: "Skin Rash" },
  { emoji: "🦴", label: "Limping" },
];

const BREED_CARDS = [
  {
    img: hound,
    name: "Srilankan Hound",
    note: "Athletic, loyal, short coat",
    alt: "A Sri Lankan Hound being hugged cheek to cheek by its owner",
  },
  {
    img: golden,
    name: "Golden Retriever",
    note: "Gentle, playful, water-loving",
    alt: "A Golden Retriever hugging a smiling man in golden evening light",
  },
  {
    img: collie,
    name: "Border Collie",
    note: "Brilliant, energetic, keen",
    alt: "A child hugging a Border Collie in a sunny grass field",
  },
];

const BREED_IMAGES: Record<string, { img: string; alt: string }> = {
  "Srilankan Hound": {
    img: hound,
    alt: "A Sri Lankan Hound being hugged cheek to cheek by its owner",
  },
  "Malay Pointer": {
    img: pointer,
    alt: "A Malay Pointer hugged by its smiling owner in a sunny garden",
  },
  "Indie Native Dog": {
    img: indie,
    alt: "A child hugging a tan Sri Lankan indie native dog at golden hour",
  },
  "Golden Retriever": {
    img: golden,
    alt: "A Golden Retriever hugging a smiling man in golden evening light",
  },
  "Labrador Retriever": {
    img: labrador,
    alt: "A yellow Labrador Retriever being kissed and hugged by its owner",
  },
  "Border Collie": {
    img: collie,
    alt: "A child hugging a Border Collie in a sunny grass field",
  },
};


function Index() {
  const [breed, setBreed] = useState(BREEDS[0]);
  const [age, setAge] = useState("3");
  const [weight, setWeight] = useState("24");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm Dr. Paws, here for your dog. Tell me what's going on — try a quick symptom below. 🐾",
    },
  ]);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    threadRef.current?.scrollTo({
      top: threadRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function send(text: string) {
    const message = text.trim();
    if (!message || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: message }]);
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/ask-vet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, breed }),
      });
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const data = await res.json();
      const reply =
        typeof data === "string"
          ? data
          : (data.answer ?? data.response ?? data.message ?? JSON.stringify(data));
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "I couldn't reach the vet service right now. Please make sure it's running and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const fieldClass =
    "rounded-xl bg-card/70 px-3 py-2.5 text-sm ring-1 ring-card/70 backdrop-blur-xl outline-none focus:ring-2 focus:ring-brand/50";

  return (
    <div className="relative min-h-screen w-full overflow-hidden text-ink selection:bg-brand/20">
      <div className="pointer-events-none fixed inset-0 bg-gradient-to-br from-mist via-secondary to-accent/15" />
      <div className="pointer-events-none absolute -top-24 -left-20 size-[460px] rounded-full bg-brand/25 blur-3xl" />
      <div className="pointer-events-none absolute top-1/3 -right-16 size-[420px] rounded-full bg-accent/20 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 size-[380px] rounded-full bg-teal/25 blur-3xl" />

      <div className="relative mx-auto max-w-6xl px-5 py-8 lg:px-8">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid size-11 place-items-center rounded-2xl bg-card/50 text-xl shadow-sm ring-1 ring-card/60 backdrop-blur-xl">
              🐾
            </div>
            <div>
              <h1 className="font-display text-2xl font-bold leading-none tracking-tight">
                Know Your Dog
              </h1>
              <p className="mt-1 text-xs font-medium text-ink/50">
                Your friendly vet copilot
              </p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full bg-card/40 px-4 py-2 text-sm font-medium text-ink/70 ring-1 ring-card/60 backdrop-blur-xl sm:flex">
            <span className="size-2 rounded-full bg-teal-ink" /> Vet online
          </div>
        </header>

        <div className="mt-8 grid gap-5 lg:grid-cols-[1fr_340px]">
          <section className="flex flex-col rounded-3xl bg-card/40 p-4 shadow-xl shadow-brand/10 ring-1 ring-card/60 backdrop-blur-2xl sm:p-5">
            <div className="flex flex-wrap gap-2 border-b border-card/50 pb-4">
              <span className="rounded-full bg-brand/10 px-3 py-1.5 text-xs font-semibold text-brand">
                🐶 {breed}
              </span>
              <span className="rounded-full bg-accent/15 px-3 py-1.5 text-xs font-semibold text-accent-ink">
                {age || "—"} yrs
              </span>
              <span className="rounded-full bg-teal/20 px-3 py-1.5 text-xs font-semibold text-teal-ink">
                {weight || "—"} kg
              </span>
            </div>

            <div
              ref={threadRef}
              className="mt-4 flex max-h-[52vh] min-h-[280px] flex-col gap-4 overflow-y-auto pr-1"
            >
              {messages.map((m, i) =>
                m.role === "user" ? (
                  <div
                    key={i}
                    className="max-w-[70%] self-end rounded-2xl rounded-tr-md bg-brand px-4 py-3 text-sm text-primary-foreground shadow-lg shadow-brand/25"
                  >
                    {m.content}
                  </div>
                ) : (
                  <div
                    key={i}
                    className="max-w-[85%] self-start rounded-2xl rounded-tl-md bg-card/70 px-4 py-3 text-sm shadow-sm ring-1 ring-card/70 backdrop-blur-xl"
                  >
                    <div className="[&_a]:text-brand [&_a]:underline [&_code]:rounded [&_code]:bg-mist [&_code]:px-1 [&_h1]:font-semibold [&_h2]:font-semibold [&_h3]:font-semibold [&_li]:marker:text-brand/60 [&_ol]:mt-2 [&_ol]:list-decimal [&_ol]:space-y-1 [&_ol]:pl-4 [&_ol]:text-ink/70 [&_p+p]:mt-2 [&_strong]:font-semibold [&_strong]:text-ink [&_ul]:mt-2 [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-4 [&_ul]:text-ink/70">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {m.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ),
              )}

              {loading && (
                <div className="flex items-center gap-3 self-start rounded-2xl rounded-tl-md bg-card/60 px-4 py-3 shadow-sm ring-1 ring-card/70 backdrop-blur-xl">
                  <span className="size-4 animate-spin rounded-full border-2 border-brand/30 border-t-brand" />
                  <span className="text-sm text-ink/40">Dr. Paws is typing…</span>
                </div>
              )}
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {SYMPTOMS.map((s) => (
                <button
                  key={s.label}
                  type="button"
                  disabled={loading}
                  onClick={() => send(`My dog is showing signs of ${s.label.toLowerCase()}. What should I do?`)}
                  className="rounded-full bg-card/70 px-3.5 py-2 text-sm font-medium text-ink/80 shadow-sm ring-1 ring-card/70 backdrop-blur-xl transition-transform hover:bg-card active:scale-95 disabled:opacity-50"
                >
                  {s.emoji} {s.label}
                </button>
              ))}
            </div>

            <form
              className="mt-4 flex items-center gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your dog's health…"
                className="min-w-0 flex-1 rounded-2xl bg-card/70 px-4 py-3 text-sm text-ink placeholder:text-ink/40 shadow-sm ring-1 ring-card/70 backdrop-blur-xl outline-none focus:ring-2 focus:ring-brand/50"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                aria-label="Send message"
                className="grid size-12 shrink-0 place-items-center rounded-2xl bg-brand text-lg text-primary-foreground shadow-lg shadow-brand/30 transition-opacity disabled:opacity-40"
              >
                ➤
              </button>
            </form>
          </section>

          <aside className="flex flex-col gap-5">
            <div className="rounded-3xl bg-card/40 p-5 shadow-xl shadow-brand/10 ring-1 ring-card/60 backdrop-blur-2xl">
              <h2 className="font-display text-lg font-semibold">Dog profile</h2>
              <div className="mt-4 flex flex-col gap-4">
                <label className="flex flex-col gap-1.5">
                  <span className="text-xs font-semibold uppercase tracking-wider text-ink/45">
                    Breed
                  </span>
                  <select
                    value={breed}
                    onChange={(e) => setBreed(e.target.value)}
                    className={fieldClass}
                  >
                    {BREEDS.map((b) => (
                      <option key={b}>{b}</option>
                    ))}
                  </select>
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <label className="flex flex-col gap-1.5">
                    <span className="text-xs font-semibold uppercase tracking-wider text-ink/45">
                      Age
                    </span>
                    <input
                      type="number"
                      min="0"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      className={fieldClass}
                    />
                  </label>
                  <label className="flex flex-col gap-1.5">
                    <span className="text-xs font-semibold uppercase tracking-wider text-ink/45">
                      Weight (kg)
                    </span>
                    <input
                      type="number"
                      min="0"
                      value={weight}
                      onChange={(e) => setWeight(e.target.value)}
                      className={fieldClass}
                    />
                  </label>
                </div>
              </div>
            </div>

            <div className="rounded-3xl bg-card/40 p-5 shadow-xl shadow-brand/10 ring-1 ring-card/60 backdrop-blur-2xl">
              <h2 className="font-display text-lg font-semibold">Meet our breeds</h2>
              <div className="mt-4 flex flex-col gap-3">
                {BREED_CARDS.map((b) => (
                  <div key={b.name} className="flex items-center gap-3">
                    <img
                      src={b.img}
                      alt={b.alt}
                      loading="lazy"
                      width={512}
                      height={512}
                      className="size-14 shrink-0 rounded-2xl object-cover ring-1 ring-card/70"
                    />
                    <div>
                      <p className="text-sm font-semibold">{b.name}</p>
                      <p className="text-xs text-ink/50">{b.note}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
