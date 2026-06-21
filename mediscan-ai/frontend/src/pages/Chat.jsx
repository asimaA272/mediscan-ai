import React, { useState, useRef, useEffect } from 'react'
import { Send, Smile } from 'lucide-react'
import { sendChat, detectEmotion } from '../services/api'

const QUICK_CHIPS = [
  'What does pulmonary opacity mean?',
  'Explain tuberculosis',
  'What is a pleural effusion?',
  'How accurate is AI X-ray detection?',
]

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hi, I'm MediScan AI. Ask me anything about X-rays, findings, or conditions." },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [emotion, setEmotion] = useState('Neutral')
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleInputChange = (e) => {
    const value = e.target.value
    setInput(value)
    if (value.trim().length > 3) {
      detectEmotion(value)
        .then((res) => setEmotion(res.data.emotion))
        .catch(() => {})
    } else {
      setEmotion('Neutral')
    }
  }

  const handleSend = async (text) => {
    const messageText = text || input
    if (!messageText.trim()) return

    setMessages((prev) => [...prev, { role: 'user', text: messageText }])
    setInput('')
    setLoading(true)

    try {
      const res = await sendChat(messageText)
      setMessages((prev) => [...prev, { role: 'assistant', text: res.data.reply }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Sorry, I could not reach the AI service. Is the backend running?' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto flex flex-col h-screen">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold tracking-tight">AI Chat</h1>
          <p className="text-muted text-sm mt-1">Ask about findings, conditions, or how the pipeline works.</p>
        </div>
        <div className="flex items-center gap-2 bg-bg-panel border border-line rounded-full px-3 py-1.5">
          <Smile size={14} className="text-accent-amber" />
          <span className="text-xs text-muted">Mood: <span className="text-[#E5EAF2] font-medium">{emotion}</span></span>
        </div>
      </header>

      {/* Quick chips */}
      <div className="flex gap-2 flex-wrap mb-4">
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip}
            onClick={() => handleSend(chip)}
            className="text-xs px-3 py-1.5 rounded-full border border-line text-muted hover:text-accent-cyan hover:border-accent-cyan/50 transition-colors"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-bg-panel border border-line rounded-xl p-5 space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-accent-cyan text-bg'
                  : 'bg-bg-elevated text-[#E5EAF2]'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-bg-elevated rounded-xl px-4 py-2.5 text-sm text-muted">Thinking...</div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={handleInputChange}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a medical question..."
          className="flex-1 bg-bg-panel border border-line rounded-lg px-4 py-2.5 text-sm outline-none focus:border-accent-cyan/50"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 rounded-lg bg-accent-cyan text-bg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-accent-cyan/90 transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
