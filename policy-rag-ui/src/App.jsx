import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question })
      });

      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setAnswer("❌ Failed to fetch answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>📄 Policy RAG Chatbot</h1>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a policy question..."
      />

      <button onClick={askQuestion}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div className="answer-box">
          <div className="answer-title">Answer</div>
          {answer}
        </div>
      )}
    </div>
  );
}

export default App;
