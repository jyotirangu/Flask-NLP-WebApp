import { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate  } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaEye, FaEyeSlash } from 'react-icons/fa'; 
import "./LoginRegister.css"

const API_URL = import.meta.env.VITE_API_BASE_URL;

function Register() {
  const [user, setUser] = useState({
    user_name: '',
    user_email: '',
    user_password: '',
    confirm_password: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { user_name, user_email, user_password, confirm_password } = user;

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(user_email)) {
      toast.error("Invalid email format");
      return;
    }

    if (!passwordRegex.test(user_password)) {
      toast.error("Password must be at least 8 characters, include capital, lowercase, number, and special character ❌");
      return;
    }

    if (user_password !== confirm_password) {
      toast.error("Passwords do not match");
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/api/register`, user);
      if (response.data.success) {
        toast.success(response.data.message + ' ✅');
        setUser({ user_name: '', user_email: '', user_password: '', confirm_password: '' });

        setTimeout(() => navigate('/login'), 1000);
      } else {
        toast.error(response.data.message || 'Registration failed ❌');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || "Something went wrong ❌");
    }
  };

  return (
    <div className="lr-container">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="user_name"
          placeholder="Name"
          value={user.user_name}
          onChange={handleChange}
          required
        />
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
            type={showPassword ? "text" : "password"}
            name="user_password"
            placeholder="Password"
            value={user.user_password}
            onChange={handleChange}
            required
          />
          <span onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
        </div>

        <div className="password-wrapper">
          <input
            type={showConfirmPassword ? "text" : "password"}
            name="confirm_password"
            placeholder="Confirm Password"
            value={user.confirm_password}
            onChange={handleChange}
            required
          />
          <span onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
          </span>
        </div>

        <button type="submit">Register</button>
      </form>

      <Link to="/login" className="lr-link">Already have an account? Login</Link>
    </div>
  );
}

export default Register;



