import MapView from "../components/MapView";

export default function Results({ setPage, places }) {

  console.log("RESULTS:", places);

  return (
    <div style={{ padding: "20px" }}>

      <h1>Results Page</h1>

      <MapView places={places} />

      <button onClick={() => setPage("home")}>
        Back
      </button>

    </div>
  );
}