import { useState, useEffect } from "react";
import MapView from "../components/MapView";


export default function Results({
  setPage,
  places,

  interests,
  preferences,
  duration,

  selectedPlaces,
  setSelectedPlaces,

  selectedHotel,
  setSelectedHotel,

  optimizedRoute,
  setOptimizedRoute,
}) {
  const [hotelMode, setHotelMode] = useState(false);
  const [hotelQuery, setHotelQuery] = useState("");
  const [hotels, setHotels] = useState([]);
  const [hotelResults, setHotelResults] = useState([]);

  const fetchHotels = async () => {
  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/recommendations/hotels"
    );

    const data = await response.json();

    setHotels(Array.isArray(data) ? data : []);

  } catch (error) {
    console.error("Failed to fetch hotels:", error);
  }
};
useEffect(() => {
  fetchHotels();
}, []);
const searchHotels = async (query) => {

  if (!query) {
    setHotelResults([]);
    return;
  }

  try {

    const response = await fetch(
      `http://127.0.0.1:8000/api/recommendations/hotels?query=${query}`
    );

    const data = await response.json();

    console.log("HOTEL SEARCH:", data);

    setHotelResults(data.hotels || []);

  } catch (error) {
    console.error("Hotel search failed:", error);
  }
};


  console.log("RESULTS:", places);
  places.forEach((p) => {
  console.log("PLACE ID:", p.id, p.name);
});

  const togglePlaceSelection = (place) => {

  console.log("CLICKED PLACE:", place);
  console.log("SELECTED BEFORE:", selectedPlaces);


    const exists = selectedPlaces.some(
      (p) => p.id === place.id
    );

    if (exists) {
      setSelectedPlaces(
        selectedPlaces.filter(
          (p) => p.id !== place.id
        )
      );
    } else {
      setSelectedPlaces([...selectedPlaces, place]);
    }
  };
const handleBuildRoute = async () => {
  console.log("RESULTS selectedHotel:", selectedHotel);
  console.log("RESULTS selectedPlaces:", selectedPlaces);
  try {

    const buildBody = {
      days: Number(duration),
      hotel: selectedHotel,
      places: selectedPlaces,
    };

     console.log(
      "BUILD BODY:",
      JSON.stringify(buildBody, null, 2)
    );

    const response = await fetch(
      "http://127.0.0.1:8000/api/trips/optimize",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(buildBody),
      }
    );

    console.log("STATUS:", response.status);

    const data = await response.json();

    console.log("OPTIMIZE RESPONSE:", data);

    setOptimizedRoute(data.dailyRoutes || []);

  } catch (error) {
    console.error("Route optimization failed:", error);
  }
};
  const mockTimes = [
    "09:00",
    "10:30",
    "12:00",
    "14:00",
    "16:00",
    "18:00",
  ];

  return (
    <div className="min-h-screen bg-slate-100 p-6">

      <div className="flex gap-6 h-[90vh]">

        {/* LEFT SIDE */}

        <div className="w-[35%] bg-white rounded-3xl shadow-xl p-6 overflow-y-auto">

          <div className="flex justify-between items-center mb-6">

            <h1 className="text-3xl font-bold text-slate-800">
              Your Trip
            </h1>

           <button
  onClick={handleBuildRoute}
  className="bg-sky-500 hover:bg-sky-600 text-white px-5 py-2 rounded-xl transition"
>
  Build Route
</button>

          </div>

          {/* TRIP PROFILE */}

          <div className="bg-white rounded-2xl p-5 shadow-lg mb-6">

            <h2 className="text-2xl font-bold text-slate-800 mb-4">
              Trip Profile
            </h2>

            {/* INTERESTS */}

            <div className="mb-4">

              <p className="font-semibold text-slate-700 mb-2">
                Interests
              </p>

              <div className="flex flex-wrap gap-2">

                {interests.map((item) => (
                  <span
                    key={item}
                    className="bg-sky-500 text-white px-3 py-1 rounded-full text-sm"
                  >
                    {item}
                  </span>
                ))}

              </div>

            </div>

            {/* PREFERENCES */}

            <div>

              <p className="font-semibold text-slate-700 mb-2">
                Accessibility Preferences
              </p>

              <div className="flex flex-wrap gap-2">

                {[
                  {
                    key: "wheelchairAccessible",
                    label: "♿ Wheelchair Accessible",
                  },
                  {
                    key: "lowWalking",
                    label: "🚶 Low Walking",
                  },
                  {
                    key: "asthmaFriendly",
                    label: "🌬 Asthma Friendly",
                  },
                  {
                    key: "avoidCrowds",
                    label: "👥 Avoid Crowds",
                  },
                  {
                    key: "elderlyFriendly",
                    label: "🧓 Elderly Friendly",
                  },
                ]
                  .filter((item) => preferences[item.key])
                  .map((item) => (

                    <span
                      key={item.key}
                      className="bg-emerald-500 text-white px-3 py-1 rounded-full text-sm"
                    >
                      {item.label}
                    </span>

                  ))}

              </div>

            </div>

          </div>

          {/* PLACES LIST */}

          <div className="flex flex-col gap-4">

            {places.map((place, index) => {

              const isSelected = selectedPlaces.some(
                (p) => p.id === place.id
              );

              return (

                <div
                  key={place.id}
                  className={`rounded-2xl p-4 shadow-md hover:shadow-xl transition border-2 ${
                    isSelected
                      ? "bg-green-50 border-green-400"
                      : "bg-slate-50 border-transparent"
                  }`}
                >

                  <div className="flex items-start justify-between">

                    <div>

                      <p className="text-sky-500 font-bold text-sm mb-1">
                        {mockTimes[index % mockTimes.length]}
                      </p>

                      <h2 className="text-xl font-semibold text-slate-800">
                        {place.name}
                      </h2>

                      <p className="text-slate-500 mt-1">
                        {place.category || "Travel Destination"}
                      </p>

                    </div>

                    <div className="w-4 h-4 rounded-full bg-sky-500 mt-2"></div>

                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">

                    <span className="bg-sky-100 text-sky-700 px-3 py-1 rounded-full text-xs">
                      🚶 12 min walk
                    </span>

                    <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs">
                      ♿ Accessible
                    </span>

                  </div>

                  <button
                    onClick={() => togglePlaceSelection(place)}
                    
                    className={`mt-4 px-4 py-2 rounded-xl transition-all duration-300 ${
                      isSelected
                        ? "bg-green-500 text-white"
                        : "bg-slate-200 text-slate-800"
                    }`}
                  >
                    {isSelected ? "Selected ✓" : "Select Place"}
                  </button>

                </div>

              );
            })}

          </div>

        </div>

        {/* RIGHT SIDE */}

        {/* RIGHT SIDE */}

<div className="flex-1 flex flex-col gap-4">

  {/* MAP */}

  <div className="flex-1 rounded-3xl overflow-hidden shadow-xl">

    <MapView
  places={places}
  hotels={hotels}
  optimizedRoute={optimizedRoute}

  selectedHotel={selectedHotel}
  setSelectedHotel={setSelectedHotel}

  hotelMode={hotelMode}
/>

  </div>
<div className="bg-white rounded-3xl shadow-xl p-5 mb-6">

  <div className="flex items-center justify-between mb-4">

    <h2 className="text-2xl font-bold text-slate-800">
      Selected Hotel
    </h2>
    <input
    
  type="text"
  placeholder="Search hotel..."
  value={hotelQuery}
  
onChange={(e) => {
  setHotelQuery(e.target.value);
  searchHotels(e.target.value);
}}
  className="w-full mt-4 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-400"
/>
{hotelResults.length > 0 && (

  <div className="mt-3 bg-white border border-slate-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">

    {hotelResults.map((hotel) => (

      <button
        key={hotel.id}

       onClick={() => {

  setSelectedHotel(hotel);

  setHotelResults([]);

  setHotelQuery(hotel.name);

  setHotelMode(false);

}}

        className="w-full text-left px-4 py-3 hover:bg-slate-100 transition"
      >
        🏨 {hotel.name}
      </button>

    ))}

  </div>

)}

    <button
      onClick={() => setHotelMode(!hotelMode)}
      className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-xl transition"
    >
      {hotelMode ? "Cancel" : "Choose Hotel"}
    </button>

  </div>

  {selectedHotel ? (

    <div className="bg-indigo-100 text-indigo-700 px-4 py-3 rounded-xl">
      {selectedHotel.name}
    </div>

  ) : (

    <p className="text-slate-500">
      No hotel selected.
    </p>

  )}

</div>
  {/* SELECTED PLACES PANEL */}

  <div className="bg-white rounded-3xl shadow-xl p-5">

    <div className="flex items-center justify-between mb-4">

      <h2 className="text-2xl font-bold text-slate-800">
        Selected Places ({selectedPlaces.length})
      </h2>

      <button
        className="bg-sky-500 hover:bg-sky-600 text-white px-5 py-2 rounded-xl transition"
      >
        Build Route
      </button>

    </div>

    {selectedPlaces.length === 0 ? (

      <p className="text-slate-500">
        No places selected yet.
      </p>

    ) : (

      <div className="flex flex-wrap gap-2">

        {selectedPlaces.map((place) => (

          <div
            key={place.id}
            className="bg-sky-100 text-sky-700 px-4 py-2 rounded-full"
          >
            {place.name}
          </div>

        ))}

            </div>

          )}

         </div>

        </div>

      </div>

    </div>
  );
}