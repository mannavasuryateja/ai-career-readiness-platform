import { useContext, useEffect } from "react";
import { ResultContext } from "../../context/ResultContext";
import { useNavigate } from "react-router-dom";
import ScoreCircle from "../../components/resume/ScoreCircle";
import ScoreBreakdown from "../../components/resume/ScoreBreakdown";
import SkillTags from "../../components/resume/SkillTags";
import GapClassification from "../../components/resume/GapClassification";
import ExplanationCard from "../../components/resume/ExplanationCard";
import NeuralBackground from "../../components/resume/NeuralBackground";


const Dashboard = () => {
  const { result } = useContext(ResultContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!result) {
      navigate("/resume/upload");
    }
  }, [result, navigate]);

  if (!result) return null;

  return (
    // <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">
    <div className="min-h-screen bg-slate-950 text-white relative">

        {/* <NeuralBackground /> */}


      {/* ===== Dynamic Background Layers ===== */}

      {/* Radial Spotlight */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.15),transparent_60%)]"></div>

      {/* Moving Gradient Glow */}
      <div className="absolute w-[800px] h-[800px] bg-indigo-600/20 blur-[200px] rounded-full -top-40 -left-40"></div>
      <div className="absolute w-[800px] h-[800px] bg-purple-600/20 blur-[200px] rounded-full bottom-0 right-0"></div>

      {/* Subtle Grid Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px]"></div>

      {/* ===== Header ===== */}
      <header className="flex justify-between items-center px-16 py-8 relative z-10 backdrop-blur-md">

        <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AI Career Intelligence
        </h1>

        <div className="flex gap-8 text-sm">
          <button
            onClick={() => navigate("/resume/recommendations")}
            className="text-gray-400 hover:text-white transition"
          >
            Learning Plan
          </button>

          <button
            onClick={() => navigate("/resume/simulation")}
            className="text-gray-400 hover:text-white transition"
          >
            Simulation
          </button>

          <button
            onClick={() => navigate("/resume/upload")}
            className="text-gray-400 hover:text-white transition"
          >
            New Analysis
          </button>
        </div>
      </header>

      {/* ===== Main Content ===== */}
      <div className="px-16 pb-32 relative z-10 space-y-32">

        {/* ===== HERO SCORE ===== */}
        <section className="flex flex-col items-center text-center mt-20 space-y-12">

          <ScoreCircle score={result.final_readiness_score} />

          <div className="max-w-3xl">
            <h2 className="text-6xl font-extrabold mb-6">
              Readiness Score
            </h2>

            <p className="text-gray-400 text-xl leading-relaxed">
              Hybrid AI scoring using skill overlap, category intelligence,
              TF-IDF similarity, and deep semantic embeddings.
            </p>
          </div>

        </section>

        {/* ===== SCORE BREAKDOWN ===== */}
        <section className="max-w-7xl mx-auto space-y-12">

          <h3 className="text-4xl font-bold text-center text-indigo-400">
            Intelligence Breakdown
          </h3>

          <div className="bg-slate-900/40 backdrop-blur-2xl border border-slate-800 rounded-3xl p-12 shadow-2xl">
            <ScoreBreakdown breakdown={result.score_breakdown} />
          </div>

        </section>

        {/* ===== SKILLS SECTION ===== */}
        <section className="max-w-7xl mx-auto grid md:grid-cols-2 gap-20">

          <div className="bg-slate-900/40 backdrop-blur-2xl border border-slate-800 rounded-3xl p-12 shadow-2xl">
            <SkillTags
              title="Matched Skills"
              skills={result.matched_skills}
              color="bg-green-600"
            />
          </div>

          <div className="bg-slate-900/40 backdrop-blur-2xl border border-slate-800 rounded-3xl p-12 shadow-2xl">
            <SkillTags
              title="Missing Skills"
              skills={result.missing_skills}
              color="bg-red-600"
            />
          </div>

        </section>

        {/* ===== GAP CLASSIFICATION ===== */}
        <section className="max-w-7xl mx-auto space-y-12">

          <h3 className="text-4xl font-bold text-center text-purple-400">
            Skill Gap Intelligence
          </h3>

          <div className="bg-slate-900/40 backdrop-blur-2xl border border-slate-800 rounded-3xl p-12 shadow-2xl">
            <GapClassification
              critical={result.critical_missing}
              moderate={result.moderate_missing}
              optional={result.optional_missing}
            />
          </div>

        </section>

        {/* ===== AI EXPLANATION ===== */}
        <section className="max-w-6xl mx-auto">

          <div className="bg-slate-900/40 backdrop-blur-2xl border border-slate-800 rounded-3xl p-12 shadow-2xl">
            <ExplanationCard explanation={result.explanation} />
          </div>

        </section>

      </div>
    </div>
  );
};

export default Dashboard;
