import Webcam from 'react-webcam';
import React, { useRef } from 'react';


export  const dataURLtoFile = (dataUrl, filename) => {
    const arr = dataUrl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };


export  const sendImageToServer = (imageData) => {  
  // Tạo đối tượng FormData để gửi ảnh dưới dạng tệp
  const formData = new FormData();
  formData.append('image', dataURLtoFile(imageData, 'img.jpg'));
  return formData;
};


export const resizeImage = (dataUrl, maxWidth, maxHeight) => {
  const img = new Image();
  img.src = dataUrl;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  let width = img.width;
  let height = img.height;

  if (width > height) {
    if (width > maxWidth) {
      height *= maxWidth / width;
      width = maxWidth;
    }
  } else {
    if (height > maxHeight) {
      width *= maxHeight / height;
      height = maxHeight;
    }
  }

  canvas.width = width;
  canvas.height = height;

  ctx.drawImage(img, 0, 0, width, height);

  return canvas.toDataURL('image/jpeg', 0.8);
};




