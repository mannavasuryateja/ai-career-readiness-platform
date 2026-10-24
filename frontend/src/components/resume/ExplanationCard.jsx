const ExplanationCard = ({ explanation }) => {
  return (
    <div className="mt-10 bg-slate-900 p-6 rounded-2xl shadow-xl border border-slate-800">
      <h2 className="text-xl font-semibold mb-4">AI Explanation</h2>
      <p className="text-gray-300 leading-relaxed">{explanation}</p>
    </div>
  );
};

export default ExplanationCard;
