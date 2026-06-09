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

  const createNumberedIcon = (number) => {
    return L.divIcon({
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
        ">
          ${number}
        </div>
      `,
      className: "",
      iconSize: [32, 32],
    });
  };

  console.log("MAP DATA:", places);

  const routeCoordinates = [];

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
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* PLACE MARKERS */}
      {places
        .filter(
          (place) =>
            place &&
            !place.error &&
            place.coords &&
            place.coords.lat &&
            place.coords.lng
        )
        .map((place, index) => (
          <Marker
            key={index}
            position={[
              place.coords.lat,
              place.coords.lng,
            ]}
            icon={createNumberedIcon(index + 1)}
            eventHandlers={{
              click: () => {
                if (hotelMode) {
                  setSelectedHotel(place);
                }
              },
            }}
          >
            <Popup>{place.name}</Popup>
          </Marker>
        ))}

      {/* HOTEL MARKERS */}
      {hotels.map((hotel, index) => (
        <Marker
          key={`hotel-${index}`}
          position={[
            hotel.lat,
            hotel.lng,
          ]}
          eventHandlers={{
            click: () => {
              if (hotelMode) {
                setSelectedHotel(hotel);
              }
            },
          }}
        >
          <Popup>🏨 {hotel.name}</Popup>
        </Marker>
      ))}

      {/* ROUTE */}
      {routeCoordinates.length > 0 && (
        <Polyline
          positions={routeCoordinates}
          pathOptions={{
            color: "blue",
            weight: 5,
          }}
        />
      )}

      {/* SELECTED HOTEL */}
      {selectedHotel && (
        <Marker
          position={[
            selectedHotel.lat,
            selectedHotel.lng,
          ]}
          icon={hotelIcon}
        >
          <Popup>🏨 {selectedHotel.name}</Popup>
        </Marker>
      )}
    </MapContainer>
  );
}