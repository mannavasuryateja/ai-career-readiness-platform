import { useContext, useEffect, useMemo } from "react";
import { ResultContext } from "../../context/ResultContext";
import { useNavigate } from "react-router-dom";
import ImpactChart from "../../components/resume/ImpactChart";

const Simulation = () => {
  const { result } = useContext(ResultContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!result) navigate("/resume/upload");
  }, [result, navigate]);

  if (!result) return null;

  const baseScore = Number(result.final_readiness_score);

  // Sort by increase
  const sortedSimulations = useMemo(() => {
    return [...result.score_simulation]
      .map((item) => {
        const increase = Number(item.score_increase);
        const projected = Math.min(
          100,
          Number((baseScore + increase).toFixed(2))
        );

        return {
          ...item,
          score_increase: increase,
          projected_score: projected,
        };
      })
      .sort((a, b) => b.score_increase - a.score_increase);
  }, [result.score_simulation, baseScore]);

  const topSkill = sortedSimulations[0];

  return (
    <div className="min-h-screen bg-slate-950 text-white relative">

      {/* Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(99,102,241,0.15),transparent_50%)]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_70%,rgba(139,92,246,0.12),transparent_50%)]"></div>

      {/* Header */}
      <header className="flex justify-between items-center px-16 py-8 relative z-10">
        <h1 className="text-2xl font-semibold text-white">
          AI Simulation Lab
        </h1>

        <div className="flex gap-8 text-sm text-gray-400">
          <button onClick={() => navigate("/resume/dashboard")} className="hover:text-white transition">
            Dashboard
          </button>
          <button onClick={() => navigate("/resume/recommendations")} className="hover:text-white transition">
            Learning Plan
          </button>
          <button onClick={() => navigate("/resume/upload")} className="hover:text-white transition">
            New Analysis
          </button>
        </div>
      </header>

      <div className="px-16 py-12 space-y-20 relative z-10">

        {/* ===== Top Analytics Row ===== */}
        <div className="grid md:grid-cols-2 gap-12">

          {/* Current Score */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-3xl p-12 shadow-2xl">
            <p className="text-gray-400 text-sm uppercase tracking-widest">
              Current Readiness Score
            </p>

            <p className="mt-6 text-6xl font-extrabold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              {baseScore}%
            </p>

            <p className="mt-6 text-gray-400 leading-relaxed">
              AI-evaluated score based on hybrid skill matching,
              semantic similarity and category intelligence.
            </p>
          </div>

          {/* Top ROI Skill */}
          {topSkill && (
            <div className="bg-slate-900/60 backdrop-blur-xl border border-indigo-500/40 rounded-3xl p-12 shadow-2xl">
              <p className="text-indigo-400 text-sm uppercase tracking-widest">
                Highest ROI Opportunity
              </p>

              <h2 className="mt-6 text-3xl font-bold">
                {topSkill.skill_if_learned}
              </h2>

              <p className="mt-4 text-gray-400">
                Projected Score:
                <span className="text-purple-400 font-semibold ml-2">
                  {topSkill.projected_score}%
                </span>
              </p>

              <p className="mt-2 text-green-400 font-semibold text-lg">
                +{topSkill.score_increase.toFixed(2)}% Improvement
              </p>

              <div className="mt-8 text-4xl">🚀</div>
            </div>
          )}

        </div>

        {/* ===== Forecast Section ===== */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-3xl p-14 shadow-2xl">

          <div className="flex justify-between items-center mb-12">
            <h3 className="text-3xl font-semibold">
              Skill Impact Forecast
            </h3>

            <span className="text-gray-400 text-sm">
              Ranked by Improvement Potential
            </span>
          </div>

          <ImpactChart data={sortedSimulations} baseScore={baseScore} />

        </div>

      </div>
    </div>
  );
};

export default Simulation;