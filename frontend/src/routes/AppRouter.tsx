import { Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";
import Loading from "@/pages/Loading";
import AppLayout from "@/layouts/AppLayout";
import ForgotPass from "@/pages/ForgotPass";
import { ProtectedRoute } from "@/components/ProtectedRoute";

const Home = lazy(() => import("@/pages/Home"));
const Channel = lazy(() => import("@/pages/Channel"));
const Upload = lazy(() => import("@/pages/Upload"));
const Profile = lazy(() => import("@/pages/Profile"));
const Watch = lazy(() => import("@/pages/Watch"));
const Login = lazy(() => import("@/pages/Login"));
const Register = lazy(() => import("@/pages/Register"));
const Changelog = lazy(() => import("@/pages/Changelog"));
const Pricing = lazy(() => import("@/pages/Pricing"));
const NotFound = lazy(() => import("@/pages/NotFound"));
const ResetPass = lazy(() => import("@/pages/ResetPass"));
const Liked = lazy(() => import("@/pages/Liked"));
const History = lazy(() => import("@/pages/History"));
const WatchLater = lazy(() => import("@/pages/WatchLater"));
const Subscriptions = lazy(() => import("@/pages/Subscriptions"));
const SearchResults = lazy(() => import("@/pages/SearchResults"));
const GitHubCallback = lazy(() => import("@/pages/GitHubCallback"));
const Studio = lazy(() => import("@/pages/Studio"));

export default function AppRouter() {
    return (
        <Suspense fallback={<Loading />}>
            <Routes>
                <Route element={<AppLayout />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
                    <Route path="/watch" element={<Watch />} />
                    <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                    <Route path="/changelog" element={<Changelog />} />
                    <Route path="/pricing-table" element={<Pricing />} />
                    <Route path="/liked" element={<ProtectedRoute><Liked /></ProtectedRoute>} />
                    <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
                    <Route path="/watch-later" element={<ProtectedRoute><WatchLater /></ProtectedRoute>} />
                    <Route path="/subscriptions" element={<ProtectedRoute><Subscriptions /></ProtectedRoute>} />
                    <Route path="/search-results" element={<SearchResults />} />
                    <Route path="/studio" element={<ProtectedRoute><Studio /></ProtectedRoute>} />
                <Route path="/channel/:channel_name" element={<Channel />} />
                </Route>

                <Route path="/reset-password" element={<ResetPass />} />
                <Route path="/forgotpass" element={<ForgotPass />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/loading" element={<Loading />} />
                <Route path="/channel" element={<Navigate to="/" replace />} />

                <Route path="/auth/callback" element={<GitHubCallback />} />
                <Route path="/404" element={<NotFound />} />
                <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
        </Suspense>
    );
}
