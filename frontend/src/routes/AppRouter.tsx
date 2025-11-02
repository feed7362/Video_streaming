import {Routes, Route} from "react-router-dom";
import {lazy, Suspense} from "react";

// Lazy-load pages
const Home = lazy(() => import("@/pages/Home"));
const Upload = lazy(() => import("@/pages/Upload"));
const Profile = lazy(() => import("@/pages/Profile"));
const Watch = lazy(() => import("@/pages/Watch"));
const Login = lazy(() => import("@/pages/Login"));
const Register = lazy(() => import("@/pages/Register"));
const Changelog = lazy(() => import("@/pages/Changelog"));
const Pricing = lazy(() => import("@/pages/Pricing"));
const NotFound = lazy(() => import("@/pages/NotFound"));


export default function AppRouter() {
    return (
        <Suspense fallback={<div className="p-4 text-center">Loading...</div>}>
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
        </Suspense>
    );
}
