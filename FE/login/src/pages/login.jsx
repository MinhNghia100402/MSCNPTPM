import logo from '/home/nghialee/coding/python/Face_Recognition/FE/login/src/logo.svg';
import '../assets/scss/login.css';
import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Link, useHistory } from 'react-router-dom';
import * as requests from '/home/nghialee/coding/python/Face_Recognition/FE/login/src/untils/request';
import { IconArrowLeft, IconCheck } from '@tabler/icons-react';


function Login() {
  const webcamRef = useRef(null);
  const [name, setName] = useState("");
  const [check, setCheck] = useState("/signup");
  const confirm = useHistory();
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);

  useEffect(() => {
    const intervalId = setInterval(() => {
      sendImage();
    }, 3000);
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const handleConfirmClick = () => {
     confirm.push('/home');
  }
  const handleCancelClick = () => {
    setShowSuccessMessage(false);
  }

  const sendImage = () => {
    const imageSrc = webcamRef.current.getScreenshot();

    requests
      .post('/check', { imageSrc })
      .then((response) => {
        if (response.id != null) {
          setName(response.name);
          setShowSuccessMessage(true); // Hiển thị thành công sau khi kiểm tra
          setTimeout(() => {
            setCheck('/home'); // Chuyển đến trang Home sau khi kiểm tra thành công
          }, 2000);
        } else {
          // console.log("aaaa");
          setCheck('/signup');
          
        }
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <div className='login'>
      <div className='video-container'>
        <div className='video'>
          <div className='boder-video'>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpg"
            />
          </div>
        </div>
      </div>

      <div className='contacts'>
        <div className='btn-login'>
          {/* <button>
            <Link to={check} className="btn-singup-link"> ĐĂNG NHẬP</Link>
          </button> */}
        </div>
        <div className='btn-sigin'>
          <button >
            <Link to='/signup' className="btn-singup-link"> ĐĂNG KÍ</Link>
          </button>
        </div>
      </div>

      {/* Hiển thị "vertify" khi kiểm tra thành công */}
      {showSuccessMessage && (
        <div className='vetify'>
          <div className='vertify-content'>
            <p>ĐĂNG NHẬP THÀNH CÔNG</p>
          </div>
          <div className="nameuser">
            <p>Xin chào {name}</p>
          </div>
          <div className='vertify-symbol'>
  <div className="button-container">
    <div className="btn-comfirm" onClick={handleConfirmClick}>
      <p>Xác nhận</p>
    </div>
    <div className="btn-cancel" onClick={handleCancelClick}>
      <p>Hủy</p>
    </div>
  </div>
</div>

        </div>
      )}
    </div>
  );
}

export default Login;
