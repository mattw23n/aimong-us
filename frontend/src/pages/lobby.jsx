import { useNavigate } from "react-router-dom"
import UserPill from "../component/userPill"

// dummy data
const user = {
    name: "John Doe",
    id: 1,
    isAI: false,
}


export default function Lobby(){
    const users = [user]
    const navigate = useNavigate()

    const handleClick = () => {
        navigate("/game")
    }

    return (
        <>
        <div className="font-sans text-center mx-auto mt-20">
            <p className="text-4xl">Lobby</p>
            <p>Currently hosted on insert-network-name-here</p>
            <p>Waiting for players...</p>

            <div className="flex flex-col items-center my-10">
                {users.length > 0 ? (
                    users.map((user) => (
                        <UserPill key={user.id} user={user} />
                    ))
                ) : (
                    <p>No users in the lobby</p>
                )}

            </div>



            <button onClick={handleClick} className="p-4 rounded-xl bg-blue-500 text-white mt-4 hover:bg-blue-700"> 
                Start Game
            </button>
        </div>
        
        </>
    )
}