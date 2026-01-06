import { useState } from "react";

function ChatBox() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error("Server error");
      }

      const data = await response.json();

      // Direct answer (cache hit)
      if (data.answer) {
        setAnswer(data.answer);
        setLoading(false);
        return;
      }

      // Job flow: show quick snippets then stream final answer
      const jobId = data.job_id;
      if (data.snippets && data.snippets.length > 0) {
        setAnswer((prev) => prev + "\n\n" + data.snippets.join('\n---\n'));
      }

      const es = new EventSource(`http://127.0.0.1:8000/stream/${jobId}`);
      es.onmessage = (e) => {
        try {
          const payload = JSON.parse(e.data);
          if (payload.answer) setAnswer(payload.answer);
          else if (payload.error) setError(payload.error);
        } catch {
          setError("Failed to parse stream message");
        } finally {
          setLoading(false);
          es.close();
        }
      };
      es.onerror = () => {
        setLoading(false);
        es.close();
      };
    } catch (err) {
      setError("Failed to fetch answer. Is backend running?");
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px" }}>
      <textarea
        rows="3"
        placeholder="Ask a policy question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "100%", padding: "10px" }}
      />

      <button
        onClick={askQuestion}
        style={{
          marginTop: "10px",
          padding: "10px 20px",
          cursor: "pointer",
        }}
      >
        Ask
      </button>

      {loading && <p>⏳ Thinking...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {answer && (
        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            background: "#f5f5f5",
            whiteSpace: "pre-wrap",
          }}
        >
          <strong>Answer:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default ChatBox;
