import { useState } from "react";

const JDInput = ({ setJdFile, setJdText }) => {
  const [fileName, setFileName] = useState(null);
  const [mode, setMode] = useState("file");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    setJdFile(file);
    setJdText("");
  };

  const removeFile = () => {
    setFileName(null);
    setJdFile(null);
  };

  return (
    <div className="space-y-6">

      {/* Mode Toggle */}
      <div className="flex gap-4">
        <button
          type="button"
          onClick={() => setMode("file")}
          className={`px-4 py-2 rounded-xl transition ${
            mode === "file"
              ? "bg-indigo-600"
              : "bg-slate-800 hover:bg-slate-700"
          }`}
        >
          Upload File
        </button>

        <button
          type="button"
          onClick={() => setMode("text")}
          className={`px-4 py-2 rounded-xl transition ${
            mode === "text"
              ? "bg-purple-600"
              : "bg-slate-800 hover:bg-slate-700"
          }`}
        >
          Paste Text
        </button>
      </div>

      {/* File Mode */}
      {mode === "file" && (
        <>
          {!fileName ? (
            <div className="border-2 border-dashed border-slate-700 hover:border-purple-500 transition rounded-2xl p-8 text-center cursor-pointer bg-slate-800/40">

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="hidden"
                id="jdUpload"
              />

              <label htmlFor="jdUpload" className="cursor-pointer">
                <p className="text-gray-400">
                  Click to upload Job Description
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  PDF or DOCX
                </p>
              </label>

            </div>
          ) : (
            <div className="flex justify-between items-center bg-slate-800 border border-slate-700 rounded-xl p-4">

              <div className="flex items-center gap-3">
                📄
                <p className="text-sm text-gray-200 truncate max-w-xs">
                  {fileName}
                </p>
              </div>

              <button
                onClick={removeFile}
                className="text-red-400 hover:text-red-300 transition"
              >
                ✕
              </button>

            </div>
          )}
        </>
      )}

      {/* Text Mode */}
      {mode === "text" && (
        <textarea
          rows="8"
          placeholder="Paste job description here..."
          onChange={(e) => setJdText(e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 rounded-2xl p-6 text-gray-300 focus:outline-none focus:border-purple-500"
        />
      )}

    </div>
  );
};

export default JDInput;