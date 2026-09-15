import { createFileRoute } from "@tanstack/react-router";
import { useReducedMotion } from "framer-motion";
import { lazy, Suspense, useEffect, useRef, useState, type PointerEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { DayPicker } from "react-day-picker";
import "react-day-picker/dist/style.css";

import mascotAsset from "@/assets/know-your-dog-mascot.png.asset.json";
import hound from "@/assets/dog-sri-lankan-hound.jpg";
import golden from "@/assets/dog-golden-retriever.jpg";
import collie from "@/assets/dog-border-collie.jpg";
import pointer from "@/assets/dog-malay-pointer.jpg";
import indie from "@/assets/dog-indie.jpg";
import labrador from "@/assets/dog-labrador.jpg";
import pug from "@/assets/dog-pug.jpg";
import gsd from "@/assets/dog-german-shepherd.jpg";
import rottweiler from "@/assets/dog-rottweiler.jpg";
import beagle from "@/assets/dog-beagle.jpg";
import cocker from "@/assets/dog-cocker-spaniel.jpg";
import dachshund from "@/assets/dog-dachshund.jpg";
import husky from "@/assets/dog-husky.jpg";
import shihTzu from "@/assets/dog-shih-tzu.jpg";

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
  "Pug",
  "German Shepherd",
  "Rottweiler",
  "Beagle",
  "Cocker Spaniel",
  "Dachshund",
  "Husky",
  "Shih Tzu",
];

const SYMPTOMS = [
  { emoji: "🤮", label: "Vomiting" },
  { emoji: "😴", label: "Lethargy" },
  { emoji: "🩹", label: "Skin Rash" },
  { emoji: "🦴", label: "Limping" },
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
  Pug: {
    img: pug,
    alt: "A cute Pug being hugged by a smiling person in warm golden light",
  },
  "German Shepherd": {
    img: gsd,
    alt: "A German Shepherd being hugged by its owner in a sunny park",
  },
  Rottweiler: {
    img: rottweiler,
    alt: "A Rottweiler being hugged by its loving owner in warm afternoon light",
  },
  Beagle: {
    img: beagle,
    alt: "A Beagle being hugged by a child in a sunny garden",
  },
  "Cocker Spaniel": {
    img: cocker,
    alt: "A Cocker Spaniel being hugged by its owner in warm light",
  },
  Dachshund: {
    img: dachshund,
    alt: "A Dachshund being cuddled and hugged by its owner at home",
  },
  Husky: {
    img: husky,
    alt: "A blue-eyed Siberian Husky being hugged by its owner in the snow",
  },
  "Shih Tzu": {
    img: shihTzu,
    alt: "A fluffy Shih Tzu being hugged by its owner in a cozy home",
  },
};

const DogHero3D = lazy(() => import("@/components/DogHero3D"));

function FloatingMascot() {
  const prefersReducedMotion = useReducedMotion();
  const [hydrated, setHydrated] = useState(false);
  const [action, setAction] = useState(0);
  const pointer = useRef({ x: 0, y: 0, activeUntil: 0 });

  useEffect(() => setHydrated(true), []);

  function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
    if (prefersReducedMotion) return;
    const bounds = event.currentTarget.getBoundingClientRect();
    pointer.current = {
      x: ((event.clientX - bounds.left) / bounds.width - 0.5) * 2,
      y: ((event.clientY - bounds.top) / bounds.height - 0.5) * 2,
      activeUntil: performance.now() + 1250,
    };
  }

  function resetTilt() {
    pointer.current = { ...pointer.current, activeUntil: 0 };
  }

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Play with Dr. Paws"
      className="relative mx-auto h-64 w-full max-w-sm cursor-pointer touch-none outline-none focus-visible:ring-2 focus-visible:ring-brand/60 sm:h-72 lg:h-80"
      onPointerMove={handlePointerMove}
      onPointerLeave={resetTilt}
      onPointerCancel={resetTilt}
      onClick={() => {
        if (!prefersReducedMotion) setAction((value) => value + 1);
      }}
      onKeyDown={(event) => {
        if ((event.key === "Enter" || event.key === " ") && !prefersReducedMotion) {
          event.preventDefault();
          setAction((value) => value + 1);
        }
      }}
    >
      {!hydrated || prefersReducedMotion ? (
        <img
          src={mascotAsset.url}
          alt="Cute cream and blue puppy mascot"
          width={768}
          height={768}
          draggable={false}
          className="size-full select-none object-contain drop-shadow-xl"
        />
      ) : (
        <Suspense
          fallback={
            <img
              src={mascotAsset.url}
              alt="Cute cream and blue puppy mascot"
              width={768}
              height={768}
              className="size-full select-none object-contain drop-shadow-xl"
            />
          }
        >
          <DogHero3D pointer={pointer} action={action} />
        </Suspense>
      )}
    </div>
  );
}


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
  
  const [authEmail, setAuthEmail] = useState(typeof window !== 'undefined' ? localStorage.getItem('authEmail') || '' : '');
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/auth/google/callback`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code})
      })
      .then(res => res.json())
      .then(data => {
        if (data.user?.email) {
          localStorage.setItem('authEmail', data.user.email);
          setAuthEmail(data.user.email);
        }
        window.history.replaceState({}, document.title, window.location.pathname);
      });
    }
  }, []);

  useEffect(() => {
    if (authEmail) {
      fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/calendar/events?email=${authEmail}`)
      .then(res => res.json())
      .then(data => {
        if (data.events) {
          setEvents(data.events.map((e: any) => ({...e, date: new Date(e.date)})));
        }
      });
    }
  }, [authEmail, messages]);

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
      const endpoint = import.meta.env["VITE_API_URL"] || "http://localhost:8000/api/ask-vet";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, breed, age, weight, email: authEmail }),
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
      <div className="pointer-events-none fixed inset-0">
        {Object.entries(BREED_IMAGES).map(([name, b]) => (
          <img
            key={name}
            src={b.img}
            alt={name === breed ? b.alt : ""}
            aria-hidden={name === breed ? undefined : true}
            width={1024}
            height={640}
            className={`absolute inset-0 size-full object-cover transition-opacity duration-700 ease-out ${name === breed ? "opacity-100" : "opacity-0"
              }`}
          />
        ))}
        <div className="absolute inset-0 bg-card/55 backdrop-blur-[2px]" />
      </div>
      <div className="pointer-events-none absolute -top-24 -left-20 size-[460px] rounded-full bg-brand/15 blur-3xl" />
      <div className="pointer-events-none absolute top-1/3 -right-16 size-[420px] rounded-full bg-accent/15 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 size-[380px] rounded-full bg-teal/15 blur-3xl" />


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

        <section className="mt-4 grid min-h-[340px] items-center gap-0 md:grid-cols-[minmax(0,1fr)_minmax(340px,440px)] md:gap-6">
          <div className="max-w-2xl text-center md:text-left">
            <p className="text-sm font-semibold uppercase text-brand">A healthier, happier best friend</p>
            <h2 className="mt-2 font-display text-4xl font-bold leading-tight sm:text-5xl">
              Friendly guidance for every tail wag.
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-base leading-relaxed text-ink/70 md:mx-0">
              Tell Dr. Paws what you’ve noticed and get clear, caring next steps tailored to your dog.
            </p>
          </div>
          <FloatingMascot />
        </section>

        <div className="mt-4 grid gap-5 lg:grid-cols-[1fr_340px]">
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
              <h2 className="font-display text-lg font-semibold">Calendar</h2>
              {!authEmail ? (
                <div className="mt-4 flex flex-col items-center gap-3 text-center">
                  <p className="text-sm text-ink/70">Connect your Google Calendar to schedule vet appointments and vaccine reminders automatically.</p>
                  <button 
                    onClick={() => {
                       fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/auth/google/url`)
                       .then(r => r.json())
                       .then(d => { if (d.url) window.location.href = d.url; });
                    }}
                    className="rounded-full bg-brand px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-brand/90"
                  >
                    Connect Google Calendar
                  </button>
                </div>
              ) : (
                <div className="mt-4 flex flex-col items-center">
                  <div className="w-full flex justify-between items-center mb-3">
                    <p className="text-xs text-ink/50 truncate max-w-[150px]" title={authEmail}>{authEmail}</p>
                    <button 
                      onClick={() => { localStorage.removeItem('authEmail'); setAuthEmail(''); setEvents([]); }}
                      className="text-xs text-brand hover:underline"
                    >
                      Disconnect
                    </button>
                  </div>
                  <div className="bg-card/60 rounded-xl p-2 w-full flex justify-center">
                    <DayPicker 
                      mode="multiple"
                      selected={events.map(e => e.date)}
                      className="text-xs scale-90"
                    />
                  </div>
                  <div className="mt-4 w-full text-sm text-ink/80 flex flex-col gap-2 max-h-[200px] overflow-y-auto">
                    {events.length === 0 && <p className="text-xs text-center text-ink/50 py-2">No upcoming events.</p>}
                    {events.map((e, i) => (
                      <div key={i} className="flex flex-col rounded-lg bg-card/60 p-2 text-xs border border-card/40">
                        <strong className="text-brand line-clamp-1" title={e.summary}>{e.summary}</strong>
                        <span className="text-ink/60">{e.date.toLocaleDateString()} {e.date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

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

          </aside>
        </div>
      </div>
    </div>
  );
}
