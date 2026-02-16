import { useEffect, useRef } from 'react'
import type { ChatTurn } from '../chat/types'
import { ChatMessageItem } from './ChatMessageItem'

interface ChatMessageListProps {
  turns: ChatTurn[]
}

export function ChatMessageList({ turns }: ChatMessageListProps) {
  const endOfChatRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (turns.length < 1) return
    endOfChatRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [turns])

  return (
    <main className="chat">
      {turns.map((t) => (
        <ChatMessageItem key={t.id} turn={t} />
      ))}
      <div ref={endOfChatRef} />
    </main>
  )
}
