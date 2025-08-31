import {BrowserRouter, Routes, Route} from "react-router-dom";
import Home from "@/pages/Home";
import Upload from "@/pages/Upload";
import Profile from "@/pages/Profile";
import NavBar from "@/components/NavBar";

export default function AppRouter() {
    return (
        <BrowserRouter>
            <NavBar/>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/upload" element={<Upload/>}/>
                <Route path="/profile" element={<Profile/>}/>
            </Routes>
        </BrowserRouter>
    );
}
