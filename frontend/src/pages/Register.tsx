import {RegisterForm} from "@/components/register-form";
import {Button} from "@/components/ui/button";
import {Link} from "react-router-dom";

export default function Register() {
    return (
        <div
            className="relative container min-h-screen items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0">
            <div className="relative hidden h-full flex-col p-10 lg:flex dark:border-r">

                <div
                    className="absolute inset-0 bg-primary/5"
                    style={{
                        backgroundImage: "url(/authentication-bg.png)",
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                    }}
                />
                <div className="relative z-20 flex items-center text-lg font-medium text-white/80">
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
                        <path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3"/>
                    </svg>
                    Acme Inc
                </div>
                <div className="relative z-20 mt-auto max-w-3xl text-white/70">
                    <blockquote className="leading-normal text-balance">
                        &ldquo;This library has saved me countless hours of work and helped me deliver stunning
                        designs to my clients faster than ever before.&rdquo; - Sofia Davis
                    </blockquote>
                </div>
            </div>
            <div className="flex items-center justify-center lg:p-8">
                <Link
                    to="/login"
                    className="absolute top-4 right-4 md:top-8 md:right-8 z-50"
                >
                    <Button variant="ghost">Login</Button>
                </Link>
                <RegisterForm className="mt-18"/>
            </div>
        </div>
    )
}
