import { useEffect, useState } from "react";

const ImpactChart = ({ data }) => {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    setTimeout(() => setAnimate(true), 200);
  }, []);

  const maxProjected = Math.max(...data.map(d => d.projected_score));

  return (
    <div className="space-y-12">

      {data.map((item, index) => {
        const projectedWidth =
          (item.projected_score / maxProjected) * 100;

        const currentWidth =
          ((item.projected_score - item.score_increase) / maxProjected) * 100;

        const rankBadge =
          index === 0 ? "🥇" :
          index === 1 ? "🥈" :
          index === 2 ? "🥉" : null;

        return (
          <div
            key={index}
            className={`p-8 rounded-2xl border transition ${
              index === 0
                ? "border-indigo-500 bg-slate-900/70 shadow-xl shadow-indigo-500/20"
                : "border-slate-800 bg-slate-900/50"
            }`}
          >

            {/* Header */}
            <div className="flex justify-between items-center mb-6">

              <div className="flex items-center gap-4">
                {rankBadge && (
                  <span className="text-2xl">{rankBadge}</span>
                )}

                <div>
                  <p className="text-xl font-semibold">
                    {item.skill_if_learned}
                  </p>
                  <p className="text-sm text-gray-400">
                    Improvement: +{item.score_increase}%
                  </p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-sm text-gray-400">
                  Current → Projected
                </p>
                <p className="text-lg font-semibold">
                  {item.projected_score - item.score_increase}% →{" "}
                  <span className="text-indigo-400">
                    {item.projected_score}%
                  </span>
                </p>
              </div>

            </div>

            {/* Bar Container */}
            <div className="space-y-3">

              {/* Current Score Bar */}
              <div>
                <p className="text-xs text-gray-400 mb-1">
                  Current Score
                </p>

                <div className="relative w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gray-500 transition-all duration-1000"
                    style={{
                      width: animate ? `${currentWidth}%` : "0%",
                    }}
                  ></div>
                </div>
              </div>

              {/* Projected Score Bar */}
              <div>
                <p className="text-xs text-gray-400 mb-1">
                  Projected Score
                </p>

                <div className="relative w-full h-4 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-1000 shadow-lg shadow-purple-500/30"
                    style={{
                      width: animate ? `${projectedWidth}%` : "0%",
                    }}
                  ></div>
                </div>
              </div>

            </div>

          </div>
        );
      })}

    </div>
  );
};

export default ImpactChart;