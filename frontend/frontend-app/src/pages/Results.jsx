import MapView from "../components/MapView";

export default function Results({ setPage, data }) {
  return (
    <div>
      <h1>Results Page</h1>

      <MapView places={[]} />

      <button onClick={() => setPage("home")}>
        Back
      </button>
    </div>
  );
}