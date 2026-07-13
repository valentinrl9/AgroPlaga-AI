import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import FarmersPage from "./pages/FarmersPage";
import LoginPage from "./pages/LoginPage";
import ValidationPage from "./pages/ValidationPage";
import SiexPage from "./pages/SiexPage";
import { getToken } from "./api/client";

function RequireAuth({ children }: { children: JSX.Element }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="validacion" element={<ValidationPage />} />
        <Route path="siex" element={<SiexPage />} />
        <Route path="agricultores" element={<FarmersPage />} />
      </Route>
    </Routes>
  );
}
