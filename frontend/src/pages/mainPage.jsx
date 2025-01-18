import { useNavigate } from "react-router-dom"


export default function MainPage(){
    const navigate = useNavigate()

    const handleClick = () => {
        navigate("/lobby")
    }
    return (
        <>
        <div className="font-sans max-w-4xl mx-auto mt-20">
            <p className="text-4xl">AImong Us</p>
            <p className="text-xl">A modern unnofficial Turing Test</p>

            <button onClick={handleClick} className="p-4 rounded-xl bg-blue-500 text-white mt-4 hover:bg-blue-700"> 
                Join Lobby
            </button>
        </div>

        </>
    )
}