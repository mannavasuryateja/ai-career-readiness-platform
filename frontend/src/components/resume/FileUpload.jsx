import { useState } from "react";

const FileUpload = ({ label, onChange }) => {
  const [fileName, setFileName] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    onChange(e);
  };

  const removeFile = () => {
    setFileName(null);
    onChange({ target: { files: [] } });
  };

  return (
    <div className="space-y-4">

      <label className="block text-sm text-gray-400 mb-2">
        {label}
      </label>

      {!fileName ? (
        <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 transition rounded-2xl p-8 text-center cursor-pointer bg-slate-800/40">

          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="hidden"
            id="resumeUpload"
          />

          <label htmlFor="resumeUpload" className="cursor-pointer">
            <p className="text-gray-400">
              Click to upload or drag file here
            </p>
            <p className="text-xs text-gray-500 mt-2">
              PDF or DOCX only
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

    </div>
  );
};

export default FileUpload;