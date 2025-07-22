
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const isLoggedIn = sessionStorage.getItem("isLoggedIn") ;

  if (!isLoggedIn) {
    console.log("Redirecting to /login...");
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
