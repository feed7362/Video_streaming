import { RegisterForm } from "@/components/register-form";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function Register() {
    return (
        <div className="flex flex-col lg:flex-row min-h-screen w-full overflow-hidden">
           
            <div
                className="relative w-full lg:w-1/2 bg-cover bg-center"
                style={{ backgroundImage: "url(/authentication-bg.png)" }}
            >
                <div className="absolute inset-0 bg-black/50 lg:bg-black/30" />

                <div className="hidden lg:flex absolute inset-0 flex-col justify-between p-8 text-white z-10">
                    <div className="flex items-center text-lg font-medium">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="mr-2 h-6 w-6"
                        >
                            <path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3" />
                        </svg>
                        Acme Inc
                    </div>
                    <blockquote className="max-w-md text-white/80 leading-relaxed">
                        УThis library has saved me countless hours of work and helped me deliver
                        stunning designs to my clients faster than ever before.Ф Ч Sofia Davis
                    </blockquote>
                </div>
            </div>

            {/* ѕрава частина / форма */}
            <div className="relative flex flex-col justify-center items-center w-full lg:w-1/2 p-6">
                {/*  нопки у верхньому правому кут≥ */}
                <div className="absolute top-4 right-4 flex flex-wrap gap-2 z-50">
                    <Link to="/login">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-sm text-white lg:text-inherit bg-black/30 hover:bg-black/50 lg:bg-transparent lg:hover:bg-accent"
                        >
                            Login
                        </Button>
                    </Link>
                    <Link to="/">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-sm text-white lg:text-inherit bg-black/30 hover:bg-black/50 lg:bg-transparent lg:hover:bg-accent"
                        >
                            Home
                        </Button>
                    </Link>
                </div>

                {/* ‘орма */}
                <div className="w-full max-w-md bg-white/90 dark:bg-gray-900/90 backdrop-blur-md p-6 rounded-xl shadow-md z-20">
                    <RegisterForm />
                </div>
            </div>
        </div>
    );
}
