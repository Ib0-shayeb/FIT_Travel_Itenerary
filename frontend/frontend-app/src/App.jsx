import { useState } from "react";
import Home from "./pages/Home";
import Results from "./pages/Results";

function App() {
  const [page, setPage] = useState("home");
  const [places, setPlaces] = useState([]);

  return (
    <div>
      {page === "home" ? (
        <Home setPage={setPage} setPlaces={setPlaces} />
      ) : (
        <Results setPage={setPage} places={places} />
      )}
    </div>
  );
}

export default App;