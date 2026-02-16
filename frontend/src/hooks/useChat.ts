import { useEffect, useMemo, useRef, useState } from 'react'
import type { KeyboardEvent, RefObject } from 'react'
import { sendChatMessage, type ChatMessage } from '../api'
import type { ChatTurn } from '../chat/types'

interface UseChatResult {
  turns: ChatTurn[]
  input: string
  setInput: (value: string) => void
  isSending: boolean
  error: string | null
  inputRef: RefObject<HTMLTextAreaElement>
  onSend: () => Promise<void>
  onKeyDown: (e: KeyboardEvent<HTMLTextAreaElement>) => void
}

export function useChat(): UseChatResult {
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shouldFocusInput, setShouldFocusInput] = useState(false)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const [turns, setTurns] = useState<ChatTurn[]>([
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        "Hi! I'm the Thoughtful AI support agent. Ask me about EVA, CAM, PHIL, or Thoughtful AI's agents.",
    },
  ])

  const history: ChatMessage[] = useMemo(
    () =>
      turns
        .filter((t) => t.role === 'user' || t.role === 'assistant')
        .map((t) => ({ role: t.role, content: t.content })),
    [turns],
  )

  useEffect(() => {
    if (isSending) return
    if (!shouldFocusInput) return
    inputRef.current?.focus()
    setShouldFocusInput(false)
  }, [isSending, shouldFocusInput])

  async function onSend(): Promise<void> {
    const message = input.trim()
    if (!message || isSending) return

    setError(null)
    setIsSending(true)

    const typingTurnId = crypto.randomUUID()

    const userTurn: ChatTurn = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
    }

    const typingTurn: ChatTurn = {
      id: typingTurnId,
      role: 'assistant',
      content: '',
      isTyping: true,
    }

    setTurns((prev) => [...prev, userTurn, typingTurn])
    setInput('')

    try {
      const resp = await sendChatMessage({ message, history })
      const assistantTurn: ChatTurn = {
        id: typingTurnId,
        role: 'assistant',
        content: resp.answer,
        meta: {
          source: resp.source,
          matched_question: resp.matched_question ?? null,
          score: resp.score ?? null,
        },
      }
      setTurns((prev) => prev.map((t) => (t.id === typingTurnId ? assistantTurn : t)))
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      setError(msg)
      setTurns((prev) =>
        prev.map((t) =>
          t.id === typingTurnId
            ? {
                id: typingTurnId,
                role: 'assistant',
                content: 'Sorry — something went wrong while generating a response.',
              }
            : t,
        ),
      )
    } finally {
      setIsSending(false)
      setShouldFocusInput(true)
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void onSend()
    }
  }

  return {
    turns,
    input,
    setInput,
    isSending,
    error,
    inputRef,
    onSend,
    onKeyDown,
  }
}
