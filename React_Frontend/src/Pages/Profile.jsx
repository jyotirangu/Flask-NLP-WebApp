import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import "./Profile.css"

function Profile() {
  const navigate = useNavigate();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem('isLoggedIn');

    if (!isLoggedIn) {
      navigate('/login');
    }
  }, [navigate]);


  return (
    <div className="profile-a">
      <div className="profile-b">
        <h1 className="profile-h1">Welcome to your Profile</h1>
        <p className="profile-p">What would you like to do?</p>

        <div className="profile-cards">
          <Link to="/ner" className="profile-card">Named Entity Recognition (NER)</Link>
          <Link to="/sentiment" className="profile-card">Sentiment Analysis</Link>
          <Link to="/emotion" className="profile-card">Emotion Detection</Link>
        </div>
      </div>
    </div>
  );
}

export default Profile;

