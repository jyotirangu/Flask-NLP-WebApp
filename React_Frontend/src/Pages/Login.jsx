import { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import './LoginRegister.css'; 

const API_URL = import.meta.env.VITE_API_BASE_URL;

function Login() {
  const navigate = useNavigate();
  const [user, setUser] = useState({
    user_email: '',
    user_password: ''
  });

  const [showPassword, setShowPassword] = useState(false); 

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/login`, user, {
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.data.success) {
        toast.success('Login successful!');
        sessionStorage.setItem('isLoggedIn', 'true');
        navigate('/profile');
      } else {
        toast.error('❌ Login failed. Please try again.');
      }
    } catch (error) {
      toast.error('Invalid email or password.');
    }
  };

  const togglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className="lr-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          name="user_email"
          placeholder="Email"
          value={user.user_email}
          onChange={handleChange}
          required
        />
        <div className="password-wrapper">
          <input
            type={showPassword ? 'text' : 'password'}
            name="user_password"
            placeholder="Password"
            value={user.user_password}
            onChange={handleChange}
            required
          />
          <span className="eye-icon" onClick={togglePassword}>
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
        </div>
    
        <button type="submit">Login</button>
      </form>

      <Link to="/register" className="lr-link">Don't have an account? Register</Link>
    </div>
  );
}

export default Login;
