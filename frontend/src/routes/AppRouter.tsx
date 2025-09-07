import {Routes, Route} from "react-router-dom"
import Home from "@/pages/Home"
import Upload from "@/pages/Upload"
import Profile from "@/pages/Profile"
import NotFound from "@/pages/NotFound"
// import Watch from "@/pages/Watch"
import Login from "@/pages/Login"
import Register from "@/pages/Register"

export default function AppRouter() {
    return (
        <Routes>
            {/* General routes */}
            <Route path="/" element={<Home/>}/>

            {/* Video routes */}
            <Route path="/upload" element={<Upload/>}/>
            {/*<Route path="/watch" element={<Watch/>}/>*/}

            {/* Auth routes */}
            <Route path="/profile" element={<Profile/>}/>
            <Route path="/login" element={<Login/>}/>
            <Route path="/register" element={<Register/>}/>
            {/*<Route path="/reset-password" element={<Login/>}/>*/}
            {/*<Route path="/forgot-password" element={<Login/>}/>*/}
            {/*<Route path="/privacy" element={<Login/>}/>*/}
            {/*<Route path="/terms" element={<Login/>}/>*/}

            {/* Catch-all route */}
            <Route path="*" element={<NotFound/>}/>

        </Routes>
    );
}
