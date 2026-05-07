import { useEffect, useState } from "react";

export default function Home({ setPage, setData }) {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          "http://localhost:8000/api/recommendations/places?city=Vienna"
        );
        const data = await res.json();
        console.log(data);
        setPlaces(data.places || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>Places</h1>

      {places.map((p, index) => (
     <p key={p.id || index}>{p.name}</p>
     ))}

      <button onClick={() => setPage("results")}>
        Go to Results
      </button>
    </div>
  );
}