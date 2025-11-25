import { BrowserRouter, Routes, Route } from "react-router-dom";
import RagFrontend from "./pages/RagFrontend";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RagFrontend />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
