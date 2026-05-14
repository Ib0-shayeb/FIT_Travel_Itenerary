import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function MapView({ places }) {

  console.log("MAP DATA:", places);

  return (
    <MapContainer
      center={[45.4408, 12.3155]}
      zoom={13}
      style={{
        height: "500px",
        width: "100%",
        marginTop: "20px",
      }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {places.map((place, index) => (
        <Marker
          key={index}
          position={[place.lat, place.lng]}
        >
          <Popup>
            {place.name}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}