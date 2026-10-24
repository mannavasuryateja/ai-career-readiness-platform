import { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import Loader from "../../components/resume/Loader";
import FileUpload from "../../components/resume/FileUpload";
import JDInput from "../../components/resume/JDInput";
import { resumeApi } from "../../services/api";   // ✅ FIXED
import { ResultContext } from "../../context/ResultContext";

const Upload = () => {
  const [resume, setResume] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { setResult } = useContext(ResultContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!resume) {
      setError("Please upload your resume.");
      return;
    }

    if (!jdFile && !jdText) {
      setError("Please provide a Job Description (file or text).");
      return;
    }

    try {
      setLoading(true);

      // ✅ CALL UPDATED API
      const data = await resumeApi.analyzeResume(
        resume,
        jdFile,
        jdText
      );

      // ✅ FIX: axios already returns data directly
      setResult(data);

      console.log(data);

      navigate("/resume/dashboard");
    } catch (error) {
      console.error(error);
      setError(error.message || "Something went wrong while analyzing.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">

      {/* Glow Background */}
      <div className="absolute w-[500px] h-[500px] bg-indigo-600/20 blur-[140px] rounded-full -top-32 -left-32"></div>
      <div className="absolute w-[500px] h-[500px] bg-purple-600/20 blur-[140px] rounded-full bottom-0 right-0"></div>

      {/* Top Navigation */}
      <header className="flex justify-between items-center px-12 py-6 relative z-10">
        <Link
          to="/"
          className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent"
        >
          
        </Link>

        <Link
          to="/"
          className="text-gray-400 hover:text-white transition"
        >
          Back to Home
        </Link>
      </header>

      {/* Upload Section */}
      <div className="flex justify-center items-center px-6 mt-10 relative z-10">
        <div className="w-full max-w-3xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-3xl shadow-2xl p-12">

          {/* Title */}
          <h2 className="text-4xl font-bold mb-4 text-center">
            Upload Your Resume
          </h2>

          <p className="text-gray-400 text-center mb-10">
            Our AI will analyze your resume against job requirements
            and generate insights, skill gaps, and learning plans.
          </p>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-400 p-4 rounded-xl mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-10">

            {/* Resume Section */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-indigo-400">
                Resume
              </h3>

              <FileUpload
                label="Upload Resume (PDF / DOCX)"
                onChange={(e) => setResume(e.target.files[0])}
              />
            </div>

            {/* JD Section */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-purple-400">
                Job Description
              </h3>

              <JDInput
                setJdFile={setJdFile}
                setJdText={setJdText}
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full py-4 rounded-2xl text-lg font-semibold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:scale-105 transition transform shadow-xl shadow-indigo-500/30"
            >
              Analyze with AI
            </button>

          </form>

          {/* Loader */}
          {loading && (
            <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-md flex items-center justify-center rounded-3xl">
              <Loader />
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Upload;