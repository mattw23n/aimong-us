export default function UserPill({user}){
    return (
        <div className="rounded-xl bg-blue-100 p-2 w-48">
            {user.name}
        </div>
    )
}