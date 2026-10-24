import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const ScoreCircle = ({ score }) => {
  return (
    <div className="w-48 h-48">
      <CircularProgressbar
        value={score}
        text={`${score}%`}
        styles={buildStyles({
          textColor: "#fff",
          pathColor: "#6366f1",
          trailColor: "#1e293b",
        })}
      />
    </div>
  );
};

export default ScoreCircle;
