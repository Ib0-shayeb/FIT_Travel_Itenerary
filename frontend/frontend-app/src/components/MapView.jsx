import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

export default function MapView({
  places,
  hotels,
  optimizedRoute,
  selectedHotel,
  setSelectedHotel,
  hotelMode,
}) {
  const hotelIcon = new L.Icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/139/139899.png",
    iconSize: [40, 40],
  });

  const createNumberedIcon = (number) =>
    L.divIcon({
      html: `
        <div style="
          background:#0ea5e9;
          width:32px;
          height:32px;
          border-radius:50%;
          display:flex;
          align-items:center;
          justify-content:center;
          color:white;
          font-weight:bold;
          border:3px solid white;
          box-shadow:0 4px 10px rgba(0,0,0,0.3);
        ">${number}</div>
      `,
      className: "",
      iconSize: [32, 32],
    });
  const safetyIcon = L.divIcon({
  html: `
    <div style="
      background:#ef4444;
      width:32px;
      height:32px;
      border-radius:50%;
      display:flex;
      align-items:center;
      justify-content:center;
      color:white;
      font-weight:bold;
      border:3px solid white;
      box-shadow:0 4px 10px rgba(0,0,0,0.3);
      font-size:18px;
    ">+</div>
  `,
  className: "",
  iconSize: [32, 32],
});
  // Place'ler coords.lat/lng formatında
  const isValidPlace = (place) =>
    place &&
    !place.error &&
    place.coords &&
    typeof place.coords.lat === "number" &&
    typeof place.coords.lng === "number" &&
    isFinite(place.coords.lat) &&
    isFinite(place.coords.lng);

  // Hotel'ler düz lat/lng formatında
  const isValidHotel = (hotel) =>
    hotel &&
    !hotel.error &&
    typeof hotel.lat === "number" &&
    typeof hotel.lng === "number" &&
    isFinite(hotel.lat) &&
    isFinite(hotel.lng);

  const validPlaces = (places || []).filter(isValidPlace);
  const validHotels = (hotels || []).filter(isValidHotel);
  const validRoute = (optimizedRoute || []).filter(isValidPlace);

  // Route varsa route'u, yoksa normal places'i göster
  const displayPlaces = validRoute.length > 0
  ? validRoute.filter(p => !p.isHotel)
  : validPlaces;
  // Polyline için koordinatlar
  const routeCoordinates = validRoute.map((p) => [p.coords.lat, p.coords.lng]);

  return (
    <MapContainer
      center={[45.4408, 12.3155]}
      zoom={13}
      style={{ height: "100%", width: "100%", minHeight: "500px" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* PLACE / ROUTE MARKERS */}
      {displayPlaces.map((place, index) => (
        <Marker
          key={place.id || index}
          position={[place.coords.lat, place.coords.lng]}
          icon={createNumberedIcon(index + 1)}
          eventHandlers={{
            click: () => {
              if (hotelMode) setSelectedHotel(place);
            },
          }}
        >
          <Popup>{place.name}</Popup>
        </Marker>
      ))}

      {/* HOTEL MARKERS */}
      {validHotels.map((hotel, index) => (
        <Marker
          key={`hotel-${hotel.id || index}`}
          position={[hotel.lat, hotel.lng]}
          icon={hotelIcon}
          eventHandlers={{
            click: () => {
              if (hotelMode) setSelectedHotel(hotel);
            },
          }}
        >
          <Popup>🏨 {hotel.name}</Popup>
        </Marker>
      ))}

      {/* ROUTE LINE */}
      {routeCoordinates.length > 1 && (
        <Polyline
          positions={routeCoordinates}
          pathOptions={{ color: "blue", weight: 5 }}
        />
      )}

      {/* SELECTED HOTEL */}
      {isValidHotel(selectedHotel) && (
        <Marker
          position={[selectedHotel.lat, selectedHotel.lng]}
          icon={hotelIcon}
        >
          <Popup>🏨 {selectedHotel.name}</Popup>
        </Marker>
      )}
    </MapContainer>
  );
}