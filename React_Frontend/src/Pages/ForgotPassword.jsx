import { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import "./ForgotPassword.css";


const API_URL = import.meta.env.VITE_API_BASE_URL;

function ForgotPassword() {
  const [step, setStep] = useState(1); // 1: email, 2: otp, 3: reset
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(new Array(6).fill(""));
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const navigate = useNavigate();

  // OTP input change
const handleOtpChange = (e, index) => {
  const value = e.target.value.replace(/[^0-9]/g, ""); // only numbers allowed
  if (value.length <= 1) {
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Move focus to next box
    if (value && index < otp.length - 1) {
      document.getElementById(`otp-${index + 1}`).focus();
    }
  }
};

// Backspace aur arrow navigation
const handleOtpKeyDown = (e, index) => {
  if (e.key === "Backspace" && !otp[index] && index > 0) {
    document.getElementById(`otp-${index - 1}`).focus();
  }
};



  // Step 1: Send OTP
  const handleSendOtp = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        `${API_URL}/send-otp`,
        { email },
        { withCredentials: true } // send session cookie
      );
      toast.success('OTP sent to your email!');
      setStep(2);
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to send OTP.');
    }
  };

  // Step 2: Verify OTP
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        `${API_URL}/verify-otp`,
        // { email,otp }, 
        { email, otp: otp.join("") },

        { withCredentials: true }
      );
      if (res.data.success) {
        toast.success('OTP verified! Set your new password.');
        setStep(3);
      } else {
        toast.error(res.data.message || 'Invalid OTP.');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'OTP verification failed.');
    }
  };

  // Step 3: Reset Password
  const handleResetPassword = async (e) => {
    e.preventDefault();
    const passwordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(newPassword)) {
      toast.error(
        'Password must be at least 8 characters, include capital, lowercase, number, and special character ❌'
      );
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    try {
      const res = await axios.post(
        `${API_URL}/reset-password`,
        { email, otp, new_password: newPassword }, 
        { withCredentials: true }
      );
      if (res.data.success) {
        toast.success('Password reset successful! Please log in.');
        setTimeout(() => navigate('/login'), 1000);
      } else {
        toast.error(res.data.message || 'Failed to reset password.');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to reset password.');
    }
  };

  return (
    <div className="lr-container">
      <h2>Forgot Password</h2>
      {step === 1 && (
        <form onSubmit={handleSendOtp}>
          <input
            type="email"
            placeholder="Enter your registered email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit">Send OTP</button>
        </form>
      )}
      
      
       {step === 2 && (
       <form onSubmit={handleVerifyOtp}>
       <div className="otp-container">
        {otp.map((digit, index) => (
        <input
          id={`otp-${index}`}
          key={index}
          type="text"
          maxLength="1"
          className="otp-input"
          value={digit}   // 👈 ab value bind ho rahi hai
          onChange={(e) => handleOtpChange(e, index)}
          onKeyDown={(e) => handleOtpKeyDown(e, index)}
        />
      ))}
       </div>
       <button
       type="submit"
       className="verify-btn"
       disabled={otp.join("").length < 6}  
    >
      Verify OTP
      </button>
    </form>
  )}



      {step === 3 && (
        <form onSubmit={handleResetPassword}>
          <input
            type="password"
            placeholder="New Password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Confirm New Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <button type="submit">Reset Password</button>
        </form>
      )}
      <Link to="/login" className="lr-link">
        Back to Login
      </Link>
    </div>
  );
}

export default ForgotPassword;
