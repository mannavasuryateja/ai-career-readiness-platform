const GapClassification = ({ critical, moderate, optional }) => {
  const renderSection = (title, skills, color) => (
    <div className="bg-slate-900 p-6 rounded-2xl shadow-lg border border-slate-800">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="flex flex-wrap gap-3">
        {skills.map((skill, index) => (
          <span
            key={index}
            className={`px-4 py-2 rounded-full text-sm font-medium ${color}`}
          >
            {skill}
          </span>
        ))}
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
      {renderSection("Critical Missing", critical, "bg-red-700")}
      {renderSection("Moderate Missing", moderate, "bg-yellow-600")}
      {renderSection("Optional Missing", optional, "bg-gray-600")}
    </div>
  );
};

export default GapClassification;
