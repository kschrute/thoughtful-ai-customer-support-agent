export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  message: string
  history: ChatMessage[]
}

export interface ChatResponse {
  answer: string
  source: 'kb' | 'llm'
  matched_question?: string | null
  score?: number | null
}

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''
  const res = await fetch(`${apiBaseUrl}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed (${res.status})`)
  }

  return (await res.json()) as ChatResponse
}
