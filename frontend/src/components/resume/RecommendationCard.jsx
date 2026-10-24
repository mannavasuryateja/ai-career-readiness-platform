const RecommendationCard = ({ plan }) => {
  return (
    <div className="bg-slate-900 p-6 rounded-2xl shadow-xl border border-slate-800 hover:shadow-indigo-500/10 transition">

      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">{plan.skill}</h2>

        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            plan.priority === "High"
              ? "bg-red-600"
              : "bg-yellow-600"
          }`}
        >
          {plan.priority}
        </span>
      </div>

      {/* Recommendation */}
      <p className="mt-4 text-gray-400 leading-relaxed">
        {plan.recommendation}
      </p>

      {/* Estimated Time */}
      <div className="mt-4">
        <h3 className="font-semibold">Estimated Time</h3>
        <p className="text-gray-400">{plan.estimated_time}</p>
      </div>

      {/* Career Impact */}
      <div className="mt-4">
        <h3 className="font-semibold">Career Impact</h3>
        <p className="text-indigo-400 font-medium">
          {plan.career_impact}
        </p>
      </div>

      {/* YouTube Section */}
      {plan.youtube_links && plan.youtube_links.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-3">
            Recommended Video Tutorials
          </h3>

          <div className="grid md:grid-cols-3 gap-4">
            {plan.youtube_links.map((video, index) => (
              <a
                key={index}
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-slate-800 rounded-xl overflow-hidden hover:scale-105 transition transform"
              >
                {/* Thumbnail */}
                <img
                  src={video.thumbnail}
                  alt={video.title}
                  className="w-full h-36 object-cover"
                />

                {/* Video Info */}
                <div className="p-3">
                  <h4 className="text-sm font-semibold line-clamp-2">
                    {video.title}
                  </h4>

                  <p className="text-xs text-gray-400 mt-1">
                    {video.channel}
                  </p>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;
