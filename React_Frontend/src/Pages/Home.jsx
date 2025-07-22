import { Link } from "react-router-dom";
import './Home.css'

function Home() {
  return (
    <div className="home-page">
      <h1 className="home-page-h1">Welcome to the NLP Web App</h1>
      <p className="home-page-p">Analyze text with NER, Sentiment, and Emotion Detection tools.</p>

      <div className="home-page-div">
        <Link to="/login">
          <button className="homebtn">
            Login
          </button>
        </Link>
        <Link to="/register">
          <button className="homebtn">
            Register
          </button>
        </Link>
      </div>
    </div>
  );
}

export default Home;
