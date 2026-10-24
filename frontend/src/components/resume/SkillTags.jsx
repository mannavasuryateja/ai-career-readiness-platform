const SkillTags = ({ title, skills, color }) => {
  return (
    <div className="mt-10">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
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
};

export default SkillTags;
