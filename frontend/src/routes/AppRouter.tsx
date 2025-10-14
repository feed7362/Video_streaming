import { Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";
import Loading from "@/pages/Loading";
import AppLayout from "@/layouts/AppLayout";
import ForgotPass from "../pages/ForgotPass";

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
        <Suspense fallback={<Loading />}>
            <Routes>
                <Route element={<AppLayout />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/upload" element={<Upload />} />
                    <Route path="/watch" element={<Watch />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/changelog" element={<Changelog />} />
                    <Route path="/pricing-table" element={<Pricing />} />
                </Route>

                <Route path="/forgotpass" element={<ForgotPass />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/loading" element={<Loading />} />

                <Route path="/404" element={<NotFound />} />
                <Route path="*" element={<Navigate to="/404" replace />} />
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
                {/*<Route path="/contact" element={<Contact/>}/>*/} </Routes>
        </Suspense>
    );
}