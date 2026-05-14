
import { useState } from "react";


export default function Home({ setPage, setPlaces }) {
  const [budget, setBudget] = useState("");
  const [duration, setDuration] = useState("");
  const [interests, setInterests] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(
        "http://localhost:8000/api/recommendations/places"
      );

      const result = await response.json();

      console.log("RESULT:", result);

      setPlaces(result.places);

      setPage("results");

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
          <label>Duration:</label>

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
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
          />
        </div>

        <button type="submit">
          Generate Route
        </button>

      </form>
    </div>
  );
}