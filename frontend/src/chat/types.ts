export interface ChatTurnMeta {
  source?: 'kb' | 'llm'
  matched_question?: string | null
  score?: number | null
}

export interface ChatTurn {
  id: string
  role: 'user' | 'assistant'
  content: string
  isTyping?: boolean
  meta?: ChatTurnMeta
}
