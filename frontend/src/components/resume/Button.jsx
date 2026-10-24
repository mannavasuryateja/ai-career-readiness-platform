const Button = ({ children, onClick, type = "button" }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className="bg-indigo-600 px-6 py-3 rounded-xl hover:bg-indigo-500 transition"
    >
      {children}
    </button>
  );
};

export default Button;
