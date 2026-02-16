import type React from 'react'

interface ChatComposerProps {
  error: string | null
  input: string
  isSending: boolean
  inputRef: React.RefObject<HTMLTextAreaElement>
  setInput: (value: string) => void
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
  onSend: () => Promise<void>
}

export function ChatComposer({
  error,
  input,
  isSending,
  inputRef,
  setInput,
  onKeyDown,
  onSend,
}: ChatComposerProps) {
  return (
    <footer className="composer">
      {error ? (
        <div className="error" role="alert" aria-live="polite">
          <div className="errorBody">
            <div className="errorTitle">Request failed</div>
            <div className="errorText">{error}</div>
          </div>
        </div>
      ) : null}
      <div className="composerRow">
        <textarea
          className="input"
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask a question…"
          rows={2}
          disabled={isSending}
        />
        <button
          type="button"
          className="send"
          onClick={() => void onSend()}
          disabled={isSending || !input.trim()}
        >
          {isSending ? 'Sending…' : 'Send'}
        </button>
      </div>
      <div className="hint">Enter to send, Shift+Enter for newline</div>
    </footer>
  )
}
