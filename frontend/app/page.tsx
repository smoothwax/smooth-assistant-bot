"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi Team Smooth 👋 Ask me about Booker, reception procedures, appointments, payments, discounts, memberships, or waxing FAQs.",
    },
  ]);

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!question.trim()) return;

    const userQuestion = question;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userQuestion }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "Sorry, I could not get an answer.",
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I could not connect to the Smooth Assistant backend. Make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f4f5f2] text-[#3c3c3b] flex flex-col">
      <header className="border-b border-[#d7d8d2] bg-white px-6 py-5 shadow-sm">
        <div className="mx-auto max-w-5xl flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-[#7d8b6f] font-semibold">
              Team Smooth
            </p>
            <h1 className="text-3xl font-bold tracking-tight text-[#3c3c3b]">
              Smooth Assistant
            </h1>
            <p className="text-sm text-[#777]">
              Internal help for Booker, reception, waxing FAQs, and policies.
            </p>
          </div>
  
          <div className="rounded-full border border-[#7d8b6f] px-4 py-2 text-sm font-semibold text-[#6f7f61]">
            Staff Only
          </div>
        </div>
      </header>
  
      <section className="flex-1 mx-auto w-full max-w-5xl px-4 py-8">
        <div className="rounded-[2rem] bg-white shadow-sm border border-[#d7d8d2] min-h-[72vh] flex flex-col overflow-hidden">
          <div className="border-b border-[#e5e5df] bg-[#eef1ea] px-6 py-4">
            <h2 className="text-lg font-bold text-[#3c3c3b]">
              Get Smooth. Get Answers.
            </h2>
            <p className="text-sm text-[#777]">
              Ask a question using the Smooth reception manual.
            </p>
          </div>
  
          <div className="flex-1 space-y-4 overflow-y-auto p-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    message.role === "user"
                      ? "bg-[#7d8b6f] text-white"
                      : "bg-[#f1f1ee] text-[#3c3c3b] border border-[#e1e1dc]"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
  
            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-[#f1f1ee] px-4 py-3 text-sm text-[#777] border border-[#e1e1dc]">
                  Smooth Assistant is thinking...
                </div>
              </div>
            )}
          </div>
  
          <div className="border-t border-[#e5e5df] bg-white p-4">
            <div className="flex gap-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") sendMessage();
                }}
                placeholder="Ask about Booker, no shows, payments, Accutane, memberships..."
                className="flex-1 rounded-full border border-[#cfd3c6] bg-[#fbfbfa] px-4 py-3 text-sm outline-none focus:border-[#7d8b6f]"
              />
              <button
                onClick={sendMessage}
                disabled={loading}
                className="rounded-full bg-[#7d8b6f] px-6 py-3 text-sm font-semibold text-white hover:bg-[#6f7f61] disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}