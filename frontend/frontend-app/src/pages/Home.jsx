
import { useState } from "react";


export default function Home({
  setPage,
  setPlaces,

  interests,
  setInterests,

  preferences,
  setPreferences,

  duration,
  setDuration,
}) {
  const [budget, setBudget] = useState("");
  
  
  
const togglePreference = (key) => {
  setPreferences((prev) => ({
    ...prev,
    [key]: !prev[key],
  }))
}
const handleSubmit = async (e) => {
  e.preventDefault();
    console.log("FORM SUBMITTED");
  try {
     console.log("BEFORE FETCH");
    const response = await fetch(
  "http://127.0.0.1:8000/api/recommendations/places",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      interests,
      preferences,
      budget,
      duration,
    }),
  }
);
 console.log("AFTER FETCH");
  const result = await response.json();

console.log("RESULT:", result);
console.log(JSON.stringify(result, null, 2));

setPlaces(result.places);

    setPage("results");

  } catch (error) {
    console.error("FULL Error:", error);
  }
 };

 

   return (
    <div
    className="min-h-screen bg-cover bg-center flex items-center justify-center px-4"
    style={{
      backgroundImage:
          "url('https://images.unsplash.com/photo-1514890547357-a9ee288728e0?q=80&w=1974&auto=format&fit=crop')",
    }}
    >
      <div className="absolute inset-0 bg-black/40"></div>

    <div className="relative bg-white/20 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-md border border-white/30">
   

      <h1 className="text-4xl font-bold text-white text-center mb-8">
        FIT Travel Planner
      </h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">

        <input
          type="text"
          placeholder="Enter your budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          className="p-3 rounded-xl bg-white/80 outline-none"
        />
        <input
  type="text"
  placeholder="Trip duration"
  value={duration}
  onChange={(e) => setDuration(e.target.value)}
  className="p-3 rounded-xl bg-white/80 outline-none"
/>

<div className="flex flex-wrap gap-2">

  {["History", "Food", "Nightlife", "Art", "Nature", "Shopping"].map((item) => (

    <button
      type="button"
      key={item}
      onClick={() => {
        if (interests.includes(item)) {
          setInterests(interests.filter((i) => i !== item));
        } else {
          setInterests([...interests, item]);
        }
      }}
      className={`px-4 py-2 rounded-full transition ${
        interests.includes(item)
          ? "bg-sky-500 text-white"
          : "bg-white/70 text-black"
      }`}
    >
      {item}
    </button>

  ))}

</div>
<div className="mt-10">
  <h2 className="text-2xl font-semibold text-white mb-4">
    Special Travel Preferences
  </h2>

  <div className="flex flex-wrap gap-4">

    {[
      { key: "wheelchairAccessible", label: "♿ Wheelchair Accessible" },
      { key: "lowWalking", label: " Low Walking" },
      { key: "asthmaFriendly", label: " Asthma Friendly" },
      { key: "avoidCrowds", label: " Avoid Crowds" },
      { key: "elderlyFriendly", label: " Elderly Friendly" },
    ].map((item) => (

      <button
       type="button"
        key={item.key}
        onClick={() => togglePreference(item.key)}
        className={`
          px-5 py-3 rounded-2xl backdrop-blur-md border transition-all duration-300
          ${
            preferences[item.key]
              ? "bg-white/30 border-white text-white shadow-xl scale-105"
              : "bg-white/10 border-white/20 text-white/70 hover:bg-white/20"
          }
        `}
      >
        {item.label}
      </button>

    ))}

  </div>
  
</div>
<div className="mt-6 flex flex-wrap gap-3">

  {[
    { key: "wheelchairAccessible", label: "♿ Wheelchair Accessible" },
    { key: "lowWalking", label: "🚶 Low Walking" },
    { key: "asthmaFriendly", label: "🌬 Asthma Friendly" },
    { key: "avoidCrowds", label: "👥 Avoid Crowds" },
    { key: "elderlyFriendly", label: "🧓 Elderly Friendly" },
  ]
    .filter((item) => preferences[item.key])
    .map((item) => (

      <div
        key={item.key}
        className="bg-sky-500/30 text-white px-4 py-2 rounded-full backdrop-blur-md border border-white/20"
      >
        {item.label}
      </div>

    ))}

</div>
<button
  type="submit"
  className="bg-sky-500 hover:bg-sky-600 transition text-white p-3 rounded-xl font-semibold"
>
  Generate Route
</button>

      

      </form>
    </div>
  </div>
  );
}