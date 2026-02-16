import { AppHeader, ChatComposer, ChatMessageList } from './components'
import { useChat } from './hooks/useChat'

export default function App() {
  const { turns, input, setInput, isSending, error, inputRef, onKeyDown, onSend } = useChat()

  return (
    <div className="page">
      <div className="container">
        <AppHeader />
        <ChatMessageList turns={turns} />
        <ChatComposer
          error={error}
          input={input}
          isSending={isSending}
          inputRef={inputRef}
          setInput={setInput}
          onKeyDown={onKeyDown}
          onSend={onSend}
        />
      </div>
    </div>
  )
}
