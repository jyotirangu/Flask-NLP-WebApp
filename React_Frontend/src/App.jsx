import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Register from "./Pages/Register";
import Login from "./Pages/Login";
import Profile from "./Pages/Profile";
import Home from "./Pages/Home";
import NER from "./Pages/NER";
import Sentiment from "./Pages/Sentiment";
import Emotion from "./Pages/Emotion";
import ProtectedRoute from "./components/ProtectedRoute";
import './index.css'; 

function App() {
  return (
    <Router>
      {/* ToastContainer should be at root level */}
      <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        {/* Protected Routes */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ner"
          element={
            <ProtectedRoute>
              <NER />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sentiment"
          element={
            <ProtectedRoute>
              <Sentiment />
            </ProtectedRoute>
          }
        />
        <Route
          path="/emotion"
          element={
            <ProtectedRoute>
              <Emotion />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
