// Import the functions you need from the SDKs you need
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Your web app's Firebase configuration
// For Firebase JS SDK v9 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDLXueiMiH_cLvI_tBklO8SO6jGTqiL99M",
  authDomain: "quickfix-a050e.firebaseapp.com",
  projectId: "quickfix-a050e",
  storageBucket: "quickfix-a050e.firebasestorage.app",
  messagingSenderId: "816982077331",
  appId: "1:816982077331:web:cbf82216566b444a044266",
  measurementId: "G-JTE4WVGH49"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

export default app;
