import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden relative">

      {/* Background Glow Effects */}
      <div className="absolute w-[600px] h-[600px] bg-indigo-600/20 blur-[150px] rounded-full -top-40 -left-40"></div>
      <div className="absolute w-[500px] h-[500px] bg-purple-600/20 blur-[150px] rounded-full bottom-0 right-0"></div>

      {/* Top Navigation
      <header className="flex justify-between items-center px-12 py-6 relative z-10">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AI Career Platform
        </h1>

        <div className="flex gap-6 items-center">
          <Link
            to="/resume/upload"
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-90 transition shadow-lg shadow-indigo-500/20"
          >
            Launch App
          </Link>
        </div>
      </header> */}

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 relative z-10 mt-20">

        <h2 className="text-6xl md:text-7xl font-extrabold leading-tight max-w-4xl">
          Intelligent Resume
          <span className="block bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Matching & Career AI
          </span>
        </h2>

        <p className="mt-8 text-gray-400 text-lg max-w-2xl leading-relaxed">
          A hybrid AI system that analyzes your resume against job descriptions,
          identifies skill gaps, simulates score improvements, and generates
          personalized learning plans — powered by explainable AI.
        </p>

        {/* CTA Buttons */}
        <div className="mt-10 flex gap-6">
          <Link
            to="/resume/upload"
            className="px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 text-lg font-semibold shadow-xl shadow-indigo-500/30 hover:scale-105 transition"
          >
            Get Started
          </Link>

          <a
            href="#features"
            className="px-8 py-4 rounded-2xl border border-slate-700 hover:bg-slate-800 transition text-lg"
          >
            Explore Features
          </a>
        </div>
      </section>

      {/* Feature Preview Section */}
      <section
        id="features"
        className="mt-32 px-12 pb-32 relative z-10"
      >
        <h3 className="text-4xl font-bold text-center mb-16">
          Why This Platform Is Different
        </h3>

        <div className="grid md:grid-cols-3 gap-10">

          {/* Feature Card 1 */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 p-8 rounded-3xl hover:border-indigo-500 transition shadow-lg">
            <h4 className="text-xl font-semibold mb-4 text-indigo-400">
              Hybrid AI Matching
            </h4>
            <p className="text-gray-400 leading-relaxed">
              Combines skill overlap, category mapping, TF-IDF similarity,
              and semantic embeddings for research-grade precision.
            </p>
          </div>

          {/* Feature Card 2 */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 p-8 rounded-3xl hover:border-purple-500 transition shadow-lg">
            <h4 className="text-xl font-semibold mb-4 text-purple-400">
              Explainable Intelligence
            </h4>
            <p className="text-gray-400 leading-relaxed">
              Transparent skill gap analysis with critical, moderate,
              and optional classifications for clarity.
            </p>
          </div>

          {/* Feature Card 3 */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800 p-8 rounded-3xl hover:border-pink-500 transition shadow-lg">
            <h4 className="text-xl font-semibold mb-4 text-pink-400">
              Score Simulation Engine
            </h4>
            <p className="text-gray-400 leading-relaxed">
              Predict how your readiness score improves before you
              invest time learning new skills.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
};

export default Home;
