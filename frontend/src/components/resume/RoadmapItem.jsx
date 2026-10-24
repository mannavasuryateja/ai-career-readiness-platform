import { useState } from "react";

const RoadmapItem = ({
  plan,
  isLast,
  completedSkills = [],
  toggleComplete = () => {},
}) => {
  const [open, setOpen] = useState(false);

  const isCompleted = completedSkills.includes(plan.skill);

  /* =========================
     PRIORITY STYLING
  ========================= */

  const getPriorityStyles = () => {
    if (plan.priority === "High") {
      return {
        dot: "border-red-500 bg-red-500",
        badge: "bg-red-600",
        label: "Critical",
      };
    }

    if (plan.priority === "Medium") {
      return {
        dot: "border-yellow-500 bg-yellow-500",
        badge: "bg-yellow-600",
        label: "Moderate",
      };
    }

    return {
      dot: "border-blue-500 bg-blue-500",
      badge: "bg-blue-600",
      label: "Optional",
    };
  };

  const styles = getPriorityStyles();

  return (
    <div className="relative pl-16">

      {/* Vertical Line */}
      {!isLast && (
        <div className="absolute left-6 top-12 w-[2px] h-full bg-slate-700"></div>
      )}

      {/* Timeline Dot */}
      <div
        className={`absolute left-3 top-6 w-6 h-6 rounded-full border-4 transition ${
          isCompleted
            ? "bg-green-500 border-green-500 shadow-lg shadow-green-500/40"
            : styles.dot
        }`}
      ></div>

      {/* Card */}
      <div
        className={`bg-slate-900/60 backdrop-blur-xl border rounded-2xl p-8 shadow-xl transition duration-300 ${
          isCompleted
            ? "border-green-500/50 opacity-80"
            : "border-slate-800 hover:border-indigo-500"
        }`}
      >

        {/* Header */}
        <div className="flex justify-between items-center flex-wrap gap-4">

          <div>
            <h3 className="text-2xl font-bold flex items-center gap-3">
              {plan.skill}

              {isCompleted && (
                <span className="text-green-400 text-sm font-medium">
                  ✓ Completed
                </span>
              )}
            </h3>

            <span
              className={`inline-block mt-2 px-3 py-1 rounded-full text-xs ${styles.badge}`}
            >
              {styles.label} Priority
            </span>
          </div>

          {/* Complete Button */}
          <button
            onClick={() => toggleComplete(plan.skill)}
            className={`px-4 py-2 rounded-lg text-sm transition ${
              isCompleted
                ? "bg-green-600 hover:bg-green-500"
                : "bg-slate-700 hover:bg-slate-600"
            }`}
          >
            {isCompleted ? "Completed" : "Mark Complete"}
          </button>

        </div>

        {/* Recommendation */}
        <p className="text-gray-400 mt-6 leading-relaxed">
          {plan.recommendation}
        </p>

        {/* Expand Toggle */}
        <button
          onClick={() => setOpen(!open)}
          className="mt-6 text-indigo-400 hover:text-indigo-300 transition text-sm"
        >
          {open ? "Hide Roadmap ▲" : "View Detailed Roadmap ▼"}
        </button>

        {/* Expand Section */}
        <div
          className={`overflow-hidden transition-all duration-500 ${
            open ? "max-h-[2000px] opacity-100 mt-8" : "max-h-0 opacity-0"
          }`}
        >
          <div className="border-t border-slate-800 pt-8 space-y-6">

            {/* Steps */}
            {plan.roadmap_steps.map((step, index) => (
              <div key={index} className="flex gap-4 items-start">
                <div className="w-8 h-8 flex items-center justify-center rounded-full bg-indigo-600 text-sm font-bold">
                  {index + 1}
                </div>
                <p className="text-gray-300">{step}</p>
              </div>
            ))}

            {/* Meta Info */}
            <div className="mt-6 text-sm text-gray-400 space-y-1">
              <p>⏳ {plan.estimated_time}</p>
              <p>📈 Career Impact: {plan.career_impact}</p>
            </div>

            {/* YouTube Resources */}
            {plan.youtube_links?.length > 0 && (
              <div className="mt-8">
                <h4 className="text-lg font-semibold mb-4 text-indigo-400">
                  Recommended Tutorials
                </h4>

                <div className="grid md:grid-cols-2 gap-6">
                  {plan.youtube_links.map((video, index) => (
                    <a
                      key={index}
                      href={video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group bg-slate-800 rounded-xl overflow-hidden border border-slate-700 hover:border-indigo-500 transition shadow-lg"
                    >
                      <div className="relative overflow-hidden">
                        <img
                          src={video.thumbnail}
                          alt={video.title}
                          className="w-full h-40 object-cover group-hover:scale-105 transition duration-300"
                        />

                        <div className="absolute inset-0 flex items-center justify-center bg-black/40 group-hover:bg-black/20 transition">
                          <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center shadow-lg">
                            ▶
                          </div>
                        </div>
                      </div>

                      <div className="p-4">
                        <p className="text-sm font-medium text-gray-200 line-clamp-2">
                          {video.title}
                        </p>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};

export default RoadmapItem;