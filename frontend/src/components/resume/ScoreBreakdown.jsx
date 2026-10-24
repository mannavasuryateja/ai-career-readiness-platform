const ScoreBreakdown = ({ breakdown }) => {
  const metrics = [
    { label: "Skill Overlap", value: breakdown.skill_overlap_percent },
    { label: "Category Match", value: breakdown.category_overlap_percent },
    { label: "TF-IDF Similarity", value: breakdown.tfidf_similarity_percent },
    { label: "Semantic Similarity", value: breakdown.semantic_similarity_percent },
  ];

  return (
    <div className="grid grid-cols-2 gap-6 mt-10">
      {metrics.map((metric, index) => (
        <div
          key={index}
          className="bg-slate-900 p-6 rounded-2xl shadow-lg border border-slate-800"
        >
          <h3 className="text-gray-400">{metric.label}</h3>
          <p className="text-2xl font-bold mt-2 text-indigo-400">
            {metric.value}%
          </p>
        </div>
      ))}
    </div>
  );
};

export default ScoreBreakdown;
