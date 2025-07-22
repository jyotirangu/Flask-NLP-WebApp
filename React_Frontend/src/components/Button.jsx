function Button({ text }) {
  return (
    <button
      type="submit"
      className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition"
    >
      {text}
    </button>
  );
}

export default Button;
