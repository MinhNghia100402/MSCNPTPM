let video = null;
let isLock = false;
let past_time = 0;
let time_sent_step = 2500;

const init = () => {
  const constraints = {
    // audio: true,
    video: { width: 1280, height: 720 },
  };

  navigator.mediaDevices
    .getUserMedia(constraints)
    .then((mediaStream) => {
      video = document.querySelector("video");
      video.srcObject = mediaStream;
      video.onloadedmetadata = () => {
        video.play();
      };
    })
    .catch((err) => {
      console.error(`${err.name}: ${err.message}`);
    });
};

const callAPI = (formData) => {
  fetch("http://localhost:8000/check", {
    body: formData,
    method: "post",
  })
    .then((data) => {
      return data.json();
    })
    .then((data) => {
      if (data?.msv) {
        if (!isLock) showAlert(data);
        isLock = true;
      }
    });
};

const showAlert = (data) => {
  Swal.fire({
    title: "Thành công",
    text: `Họ tên: ${data.name} -  MSV: ${data.msv}`,
    icon: "success",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Xác nhận!",
    cancelButtonText: "Huỷ",
    allowEnterKey: true,
    allowEscapeKey: true,
    didClose: () => {
      // isLock = false;
    },
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = `./home.html?name=${data.name}`
      // isLock = false;
    }
  });
};

const getImageFromCamera = () => {
  const canvas = document.getElementById("canvas");
  canvas.width = 1280;
  canvas.height = 720;

  // console.log(video);
  canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob((blob) => {
    let file = new File([blob], "img.jpg", { type: "image/jpeg" });

    let formData = new FormData();
    formData.append("file", file);

    let current_time = (new Date()).getTime();
    if (current_time - past_time > time_sent_step){
      callAPI(formData);
      past_time = current_time;
    }
  }, "image/jpeg");
};

const handlerLogin = () => {
  document.getElementById("btn-login").addEventListener("click", () => {
    past_time = 0;
    isLock = false;
  })
}

$(document).ready(function () {
  init();
  handlerLogin()
  setInterval(() => {
    if (!isLock) getImageFromCamera();
  }, 200);
});
