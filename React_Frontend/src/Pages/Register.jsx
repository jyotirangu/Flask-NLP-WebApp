import { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import "./LoginRegister.css";

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

  const [showOtp, setShowOtp] = useState(false);
  const [otp, setOtp] = useState('');
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [isEmailVerified, setIsEmailVerified] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };
  // ✅ Send OTP
  const handleSendOtp = async () => {
    if (!user.user_email) {
      toast.error("Enter email first");
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/send-otp`, { email: user.user_email }, { withCredentials: true });
      if (response.data.success) {
        toast.success("OTP sent to your email ✅");
        setShowOtpInput(true); // show OTP input field
      } else {
        toast.error(response.data.message || "Failed to send OTP ❌");
      }
    } catch (error) {
      toast.error(error.response?.data?.message || "Error sending OTP ❌");
    }
  };

   // ✅ Verify OTP
  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/verify-otp`, { email: user.user_email, otp }, { withCredentials: true });
      if (response.data.success) {
        toast.success("Email verified ✅");
        setIsEmailVerified(true);   // 👉 Mark verified
        setShowOtpInput(false);     // 👉 Hide OTP input after success
      } else {
        toast.error(response.data.message || "OTP verification failed ❌");
      }
    } catch (error) {
      toast.error(error.response?.data?.message || "Error verifying OTP ❌");
    }
  };

    const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isEmailVerified) {
      toast.error("Please verify your email first ❌");
      return;
    }

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
      const response = await axios.post(`${API_URL}/api/register`, user, { withCredentials: true });
      if (response.data.success) {
      
        toast.success("Registration successful! Please login.");
        setTimeout(() => navigate('/login'), 1500); // ✅ redirect after 1.5s
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
      {!showOtp ? (
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="user_name"
            placeholder="Name"
            value={user.user_name}
            onChange={handleChange}
            required
          />
          <div className="email-verify-wrapper">
          <input
            type="email"
            name="user_email"
            placeholder="Email"
            value={user.user_email}
            onChange={handleChange}
            required
          />
          {!isEmailVerified && (
            <button type="button" onClick={handleSendOtp} className="email-btn">
              Verify Email
            </button>
          )}
        </div>

        {/* OTP input (only visible when user clicks Verify Email) */}
        {showOtpInput && (
          <div className="otp-wrapper">
            <input
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={e => setOtp(e.target.value)}
              required
            />
            <button type="button" onClick={handleOtpSubmit} className="otp-btn">
              Submit OTP
            </button>
          </div>
        )}

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
      ) : (
        <form onSubmit={handleOtpSubmit}>
          <input
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={e => setOtp(e.target.value)}
            required
          />
          <button type="submit">Verify OTP</button>
        </form>
      )}

      {!showOtp && (
        <Link to="/login" className="lr-link">Already have an account? Login</Link>
      )}
    </div>
  );
}

export default Register;
