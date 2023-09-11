import axios from 'axios'

const requets = axios.create({
    baseURL: 'http://localhost:8000'
});

export const get = async(path,options = {}) => {
    const respone = await requets.get(path,options);
    return respone.data;
}

export const post = async(path,options = {}) => {
    const respone = await requets.post(path,options);
    // console.log(respone);
    return respone.data;
}
