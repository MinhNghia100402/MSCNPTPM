import logo from '/home/nghialee/coding/python/Face_Recognition/FE/login/src/logo.svg';
import '/home/nghialee/coding/python/Face_Recognition/FE/login/src/assets/scss/signup.css';
import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';
import Resizer from 'react-image-file-resizer';
import * as requests from '../untils/request';
import { Link, useHistory } from 'react-router-dom';
import { IconArrowLeft, IconCircleCheck } from '@tabler/icons-react';

function Signup() {
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isCapturing, setIsCapturing] = useState(true);
  const [textButton, setTextButton] = useState("a");
  const [img,setImg] = useState(null);
  const comfirm = useHistory();
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [countdown, setCountdown] = useState(3);



  const boundingBox = {
    left: 100,    // Tọa độ x của góc trên bên trái
    top: 150,     // Tọa độ y của góc trên bên trái
    width: 80,    // Chiều rộng
    height: 100   // Chiều cao
  };
  
  // const handleClickToHome = () => {
  //   confirm.push('/home')
  // };

  const drawFaceBoundingBox = (imageSrc, boundingBox) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
  
    // Tạo một hình ảnh với kích thước gốc để vẽ lên canvas
    const img = new Image();
    img.src = imageSrc;
  
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
  
      // Vẽ đường kẻ xung quanh khuôn mặt
      ctx.strokeStyle = 'red'; // Màu sắc đường kẻ
      ctx.lineWidth = 2; // Độ dày đường kẻ
      ctx.strokeRect(
        boundingBox.left,
        boundingBox.top,
        boundingBox.width,
        boundingBox.height
      );
  
      // Hiển thị canvas có đường kẻ xung quanh khuôn mặt
      const modifiedImageSrc = canvas.toDataURL('image/jpeg');
      // Đặt modifiedImageSrc vào hình ảnh đã chọn hoặc hiển thị nó bằng cách thay đổi selectedImage state của bạn.
    };
  };


  drawFaceBoundingBox(selectedImage, boundingBox); 
  

  const handleUpload = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result);
      setIsCapturing(false);
      setTextButton("Chụp ảnh");
    };
    if (file) {
      reader.readAsDataURL(file);
    }
  };
  

  const captureImage = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setSelectedImage(imageSrc);
    setIsCapturing(true);
  };
  

  const showWebcam = () => {
    setSelectedImage(null);
    setIsCapturing(true);
  };

// select values from the input values 
const [name,setName] = useState("");
const [id,setId] = useState("");
const [lop,setLop] = useState("");
const [years,setYears] = useState("");

const sendData = () => {
  if (selectedImage) {
    console.log('Image data:', selectedImage);

    const formData = new FormData();
    formData.append('image', selectedImage); // Sử dụng biến img thay vì isCapturing
    formData.append('name', name);
    formData.append('id', id);
    formData.append('class', lop);
    formData.append('year', years);

    setShowSuccessMessage(true);

    const countdownInterval = setInterval(() => {
      setCountdown((prevCountdown) => prevCountdown - 1);
    }, 1000); // Cập nhật mỗi giây

    setTimeout(() => {
      clearInterval(countdownInterval); // Dừng đếm ngược
      setShowSuccessMessage(false);
      comfirm.push('/');
    }, 3000); // 3 giây

    requests
      .post('/addnew', formData)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.error(error);
      });
  }
};



  return (
    <div className='signup-container'>
      <div className='signup-video'>
        <div className='video-process'>
          <div className='boder-video-signup'>
          {selectedImage ? (
              <img src={selectedImage} alt='Đã tải lên' />
            ) : isCapturing ? (
              <div className='webcam-background'>
                <Webcam
                  className='webcam'
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat='image/jpeg'
                />
                <div className="btn-capture">
                  <button onClick={captureImage}>Chụp </button>
                </div>
              </div>
            ) : (
              <div>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleUpload}
                  style={{ display: 'none' }}
                />
                <button className="choose-images" onClick={() => fileInputRef.current.click()}>
                  Chọn ảnh
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="information-">
        <div className="name-user">
          <div className="name">
            <p>Họ và Tên</p>
          </div>
          <div className="name-values">
            <input type="text" id='name-user' onChange={event => setName(event.target.value)}/>
          </div>
        </div>
        <div className="id-user">
          <div className="id">
            <p>Mã sinh viên</p>
          </div>
          <div className="id-values">
            <input type="text" id='studen-code' onChange={event => setId(event.target.value)}/>
          </div>
        </div>
        <div className="class-user">
          <div className="class">
            <p>Lớp</p>
          </div>
          <div className="class-values">
            <input type="text" id='class' onChange={event => setLop(event.target.value)} />
          </div>
        </div>
        <div className="years">
          <div className="years-name">
            <p>Khóa</p>
          </div>
          <div className="years-values">
            <input type="text" id='id' onChange={event => setYears(event.target.value)}/>
          </div>
        </div>
        <div className="images">
          <div className="capture">
            <button onClick={showWebcam}>Chụp ảnh</button>
          </div>
          <div className='zzz' >
            {selectedImage ? (
              <label htmlFor="" className="btn-choose-images">
                Chọn ảnh
                <input type="file" ref={fileInputRef} onInput={event => handleUpload(event)} onChange={handleUpload} />
              </label>
            ) : (
              <div className='zzz'>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleUpload}
                  style={{ display: 'none' }}
                />
                <button className="choose-images" onClick={() => fileInputRef.current.click()}>
                  Chọn ảnh
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="confirm">
          <button onClick={sendData}> XÁC NHẬN ĐĂNG KÝ</button>
        </div>
      </div>
      {showSuccessMessage && (
  <div className="success-message">
    <p className='ok'>ĐĂNG KÍ THÀNH CÔNG</p>
    <p className='kkk'>Chuyển đến trang đăng nhập trong {countdown} giây ...</p>
        <IconCircleCheck color='green' size={100}/>
  </div>
)}


    </div>
  );
};

export default Signup;

