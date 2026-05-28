import { useState } from "react";
import Home from "./pages/Home";
import Results from "./pages/Results";

function App() {
  const [page, setPage] = useState("home");

  const [places, setPlaces] = useState([]);

  const [duration, setDuration] = useState("");

  const [interests, setInterests] = useState([]);

  const [selectedPlaces, setSelectedPlaces] = useState([]);

  const [selectedHotel, setSelectedHotel] = useState(null);

  const [optimizedRoute, setOptimizedRoute] = useState([]);

  const [preferences, setPreferences] = useState({
    wheelchairAccessible: false,
    lowWalking: false,
    asthmaFriendly: false,
    avoidCrowds: false,
    elderlyFriendly: false,
  });

  return (
    <div>
      {page === "home" ? (
        <Home
          setPage={setPage}
          setPlaces={setPlaces}

          interests={interests}
          setInterests={setInterests}

          preferences={preferences}
          setPreferences={setPreferences}

          duration={duration}
          setDuration={setDuration}
        />
      ) : (
        <Results
          setPage={setPage}

          places={places}

          interests={interests}

          preferences={preferences}

          selectedPlaces={selectedPlaces}
          setSelectedPlaces={setSelectedPlaces}

          selectedHotel={selectedHotel}
          setSelectedHotel={setSelectedHotel}

          optimizedRoute={optimizedRoute}
          setOptimizedRoute={setOptimizedRoute}
        />
      )}
    </div>
  );
}

export default App;