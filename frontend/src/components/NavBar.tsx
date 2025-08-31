import {Link} from "react-router-dom";
import {ModeToggle} from "@/components/mode-toggle";

export default function NavBar() {
    return (
        <nav className="p-4 bg-gray-100 dark:bg-gray-900 flex justify-between items-center">
            {/* Left side: logo / app name */}
            <div className="flex space-x-4">
                <Link to="/" className="font-semibold">Home</Link>
                <Link to="/upload" className="font-semibold">Upload</Link>
                <Link to="/profile" className="font-semibold">Profile</Link>
            </div>

            {/* Right side: theme toggle */}
            <ModeToggle/>
        </nav>
    );
}
