import catloop from '@/media/cat-loop-gif.gif';

export default function Loading() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-black text-white">
            <img
                src={catloop}
                alt="Loading cat"
                className="w-64 h-64 object-contain"
            />
            <p className="mt-4 text-lg opacity-80">
                Please wait while we load the content for you...
            </p>
        </div>
    );
}
