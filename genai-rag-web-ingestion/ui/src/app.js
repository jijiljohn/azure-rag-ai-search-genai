import React, { useState } from "react";
import { API_URL } from "./config";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const askQuestion = async () => {
    const resp = await axios.post(`${API_URL}/chat`, { question });
    setAnswer(resp.data.answer);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>GenAI Chat</h1>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question"
        style={{ width: "50%" }}
      />
      <button onClick={askQuestion}>Ask</button>
      <div style={{ marginTop: "1rem" }}>{answer}</div>
    </div>
  );
}

export default App;
