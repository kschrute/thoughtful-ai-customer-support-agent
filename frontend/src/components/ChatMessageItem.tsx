import type { ChatTurn } from '../chat/types'

function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return ''
  return score.toFixed(3)
}

interface ChatMessageItemProps {
  turn: ChatTurn
}

export function ChatMessageItem({ turn }: ChatMessageItemProps) {
  return (
    <div className={turn.role === 'user' ? 'row rowUser' : 'row rowAssistant'}>
      <div className={turn.role === 'user' ? 'bubble bubbleUser' : 'bubble bubbleAssistant'}>
        {turn.isTyping ? (
          <output className="typing" aria-live="polite" aria-atomic="true">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </output>
        ) : (
          <div className="content">{turn.content}</div>
        )}
        {turn.role === 'assistant' && turn.meta?.source ? (
          <div className="meta">
            <span className={turn.meta.source === 'kb' ? 'badge badgeKb' : 'badge badgeLlm'}>
              {turn.meta.source === 'kb' ? 'FAQ' : 'LLM'}
            </span>
            {turn.meta.source === 'kb' && turn.meta.matched_question ? (
              <span className="metaText">
                matched: “{turn.meta.matched_question}”
                {turn.meta.score !== null && turn.meta.score !== undefined
                  ? ` (score: ${formatScore(turn.meta.score)})`
                  : ''}
              </span>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}
