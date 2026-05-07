import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

import { useState } from "react";

function App() {
  const [budget, setBudget] = useState("");
  const [duration, setDuration] = useState("");
  const [interests, setInterests] = useState("");

  const handleSubmit = async (e) => {
  e.preventDefault();

  const data = {
    budget,
    duration,
    interests,
  };

  console.log("Sending:", data);

  try {
    const response = await fetch("http://localhost:8000/route", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    console.log("Response:", result);
  } catch (error) {
    console.error("Error:", error);
  }
};

  return (
    <div style={{ padding: "20px" }}>
      <h1>Travel Planner</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Budget:</label>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
          />
        </div>

        <div>
          <label>Duration (days):</label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          />
        </div>

        <div>
          <label>Interests:</label>
          <input
            type="text"
            placeholder="e.g. food, culture"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
          />
        </div>

        <button type="submit">Generate Route</button>
      </form>
    </div>
  );
}

export default App;
