import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="flex justify-between items-center p-5 bg-slate-900 shadow-lg">
      <h1 className="text-xl font-bold text-indigo-400">
        AI Career Platform
      </h1>
      <Link
        to="/upload"
        className="bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-500"
      >
        Try Now
      </Link>
    </nav>
  );
};

export default Navbar;
