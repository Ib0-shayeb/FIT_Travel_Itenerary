import { useState } from "react";
import Home from "./pages/Home";
import Results from "./pages/Results";

export default function App() {
  const [page, setPage] = useState("home");
  const [data, setData] = useState(null);

  if (page === "home") {
    return <Home setPage={setPage} setData={setData} />;
  }

  return <Results setPage={setPage} data={data} />;
}