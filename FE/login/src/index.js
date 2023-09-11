import React from 'react';
import ReactDOM from 'react-dom'; // Sử dụng ReactDOM trực tiếp

import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

import './assets/scss/signup.css';
import Signup from './pages/signup'; // Import component Signin
import Login from './pages/login';

ReactDOM.render(
  <React.StrictMode>
    <App /> {/* Đưa component Signin vào trong đây */}
  </React.StrictMode>,
  document.getElementById('root')
);

reportWebVitals();
