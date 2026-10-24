import { useContext, useEffect, useState, useMemo } from "react";
import { ResultContext } from "../../context/ResultContext";
import { useNavigate } from "react-router-dom";
import RoadmapItem from "../../components/resume/RoadmapItem";

const Recommendations = () => {
  const { result } = useContext(ResultContext);
  const navigate = useNavigate();

  const [completedSkills, setCompletedSkills] = useState([]);

  useEffect(() => {
    if (!result) navigate("/upload");
  }, [result, navigate]);

  /* ===============================
     LOAD SAVED PROGRESS
  =============================== */
  useEffect(() => {
    const saved = localStorage.getItem("completedSkills");
    if (saved) {
      try {
        setCompletedSkills(JSON.parse(saved));
      } catch {
        setCompletedSkills([]);
      }
    }
  }, []);

  /* ===============================
     SAVE PROGRESS
  =============================== */
  useEffect(() => {
    localStorage.setItem(
      "completedSkills",
      JSON.stringify(completedSkills)
    );
  }, [completedSkills]);

  if (!result) return null;

  /* ===============================
     TOGGLE COMPLETE
  =============================== */
  const toggleComplete = (skill) => {
    setCompletedSkills((prev) =>
      prev.includes(skill)
        ? prev.filter((s) => s !== skill)
        : [...prev, skill]
    );
  };

  /* ===============================
     PROGRESS TRACKING
  =============================== */
  const totalSkills = result.learning_plan?.length || 0;

  const progressPercent =
    totalSkills > 0
      ? Math.min(
        100,
        (completedSkills.length / totalSkills) * 100
      )
      : 0;

  /* ===============================
   READINESS SIMULATION
   (FINAL FIXED VERSION)
=============================== */

  const baseScore = Number(result.final_readiness_score);

  // Create quick lookup map
  const increaseMap = useMemo(() => {
    const map = {};
    result.score_simulation.forEach((item) => {
      map[item.skill_if_learned] = Number(item.score_increase);
    });
    return map;
  }, [result.score_simulation]);

  // Sum increases cumulatively
  const totalIncreaseRaw = completedSkills.reduce((acc, skill) => {
    return acc + (increaseMap[skill] || 0);
  }, 0);

  let updatedScoreRaw = baseScore + totalIncreaseRaw;

  // ===== FINAL NORMALIZATION LOGIC =====

  // If all skills completed → force 100
  if (completedSkills.length === totalSkills) {
    updatedScoreRaw = 100;
  }

  // If very close to 100 (floating precision issue)
  if (updatedScoreRaw >= 99) {
    updatedScoreRaw = 100;
  }

  const updatedScore = Math.min(
    100,
    Number(updatedScoreRaw.toFixed(2))
  );

  const totalIncrease =
    updatedScore === 100
      ? Number((100 - baseScore).toFixed(2))
      : Number(totalIncreaseRaw.toFixed(2));

  const gapClosedPercent =
    updatedScore === 100
      ? 100
      : baseScore < 100
        ? ((updatedScore - baseScore) / (100 - baseScore)) * 100
        : 100;


  /* ===============================
     UI
  =============================== */

  return (
    <div className="min-h-screen bg-slate-950 text-white relative">

      {/* Soft Gradient Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,rgba(99,102,241,0.15),transparent_60%)]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_70%,rgba(139,92,246,0.12),transparent_60%)]"></div>

      {/* HEADER */}
      <header className="flex justify-between items-center px-16 py-8 relative z-10">
        <h1 className="text-2xl font-semibold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AI Career Upgrade Simulator
        </h1>

        <button
          onClick={() => navigate("/resume/dashboard")}
          className="text-gray-400 hover:text-white transition"
        >
          Back to Dashboard
        </button>
      </header>

      <div className="px-16 pb-24 relative z-10 space-y-24">

        {/* ===============================
            SCORE PANELS
        =============================== */}
        <div className="grid md:grid-cols-2 gap-12">

          {/* CURRENT SCORE */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-3xl p-10 shadow-2xl">
            <p className="text-sm text-gray-400 uppercase tracking-widest">
              Current Score
            </p>

            <p className="mt-6 text-5xl font-extrabold text-gray-200">
              {baseScore}%
            </p>
          </div>

          {/* UPDATED SCORE */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-indigo-500/40 rounded-3xl p-10 shadow-2xl">

            <p className="text-sm text-indigo-400 uppercase tracking-widest">
              Updated Forecast
            </p>

            <p className="mt-6 text-5xl font-extrabold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              {updatedScore}%
            </p>

            <p className="mt-4 text-green-400 font-medium">
              +{totalIncrease.toFixed(2)}% from completed skills
            </p>

            <p className="text-xs text-gray-500 mt-3">
              You have closed {gapClosedPercent.toFixed(1)}% of your skill gap
            </p>

          </div>

        </div>

        {/* ===============================
            PROGRESS BAR
        =============================== */}
        <div className="text-center space-y-6">

          <h2 className="text-3xl font-semibold">
            Learning Progress
          </h2>

          <div className="max-w-3xl mx-auto bg-slate-800 rounded-full h-4 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-700"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>

          <p className="text-gray-400">
            {completedSkills.length} / {totalSkills} Skills Completed
          </p>

        </div>

        {/* ===============================
            ROADMAP TIMELINE
        =============================== */}
        <div className="max-w-4xl mx-auto space-y-20">

          {result.learning_plan.map((plan, index) => (
            <RoadmapItem
              key={index}
              plan={plan}
              isLast={index === totalSkills - 1}
              completedSkills={completedSkills}
              toggleComplete={toggleComplete}
            />
          ))}

        </div>

      </div>
    </div>
  );
};

export default Recommendations;