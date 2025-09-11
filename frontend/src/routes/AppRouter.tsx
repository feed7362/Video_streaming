import {Routes, Route} from "react-router-dom";
import Home from "@/pages/Home";
import Upload from "@/pages/Upload";
import Profile from "@/pages/Profile";
import NotFound from "@/pages/NotFound";
import Watch from "@/pages/Watch";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Changelog from "@/pages/Changelog";
import Pricing from "@/pages/Pricing";

export default function AppRouter() {
    return (
        <Routes>
            {/* General routes */}
            <Route path="/" element={<Home/>}/>

            {/* Video routes */}
            <Route path="/upload" element={<Upload/>}/>
            <Route path="/watch" element={<Watch/>}/>

            {/* Auth routes */}
            <Route path="/profile" element={<Profile/>}/>
            {/*<Route path="/user/:userId" element={<UserProfile/>}/>*/}
            {/*<Route path="/settings" element={<Settings/>}/>*/}
            <Route path="/login" element={<Login/>}/>
            <Route path="/register" element={<Register/>}/>

            {/* Auth Helpers routers */}
            {/*<Route path="/reset-password" element={<ResetPassword/>}/>*/}
            {/*<Route path="/forgot-password" element={<ForgotPassword/>}/>*/}

            {/* Engagement routes */}
            {/*<Route path="/history" element={<WatchHistory/>}/>*/}
            {/*<Route path="/liked" element={<LikedVideos/>}/>*/}

            {/* Static Pages routers */}
            {/*<Route path="/privacy" element={<PrivacyPolicy/>}/>*/}
            {/*<Route path="/terms" element={<TermsOfService/>}/>*/}
            {/*<Route path="/about" element={<About/>}/>*/}
            {/*<Route path="/contact" element={<Contact/>}/>*/}
            <Route path="/changelog" element={<Changelog/>}/>
            <Route path="/pricing-table" element={<Pricing/>}/>

            {/* Catch-all route */}
            <Route path="*" element={<NotFound/>}/>

        </Routes>
    );
}
