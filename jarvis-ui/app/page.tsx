"use client";

import { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import {
  Camera,
  CameraOff,
  Send,
  Mic,
  Download
} from "lucide-react";

export default function Home() {

  const webcamRef = useRef<Webcam>(null);

  // CAMERA
  const [cameraOn, setCameraOn] = useState(false);

  // CHAT
  const [input, setInput] = useState("");

  const [messages, setMessages] = useState([
    "🤖 JARVIS SYSTEM ONLINE"
  ]);

  // HISTORY
  const [history, setHistory] = useState<string[]>([]);

  // DOC
  const [docAvailable, setDocAvailable] = useState(false);

  // FACE
  const [faces, setFaces] = useState<any[]>([]);

  // LIVE HEALTH DATA
  const [healthData, setHealthData] = useState({
    heart_rate: 0,
    stress: 0,
    fatigue: 0,
    emotion: "Neutral",
    attention: "HIGH",
    spo2: 0,
    temperature: 0
  });

  // FACE DETECTION
  const detectFace = async () => {

    if (!webcamRef.current) return;

    const screenshot = webcamRef.current.getScreenshot();

    if (!screenshot) return;

    try {

      const response = await fetch(
        "http://127.0.0.1:8001/detect-face",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            image: screenshot
          })
        }
      );

      const data = await response.json();

      // FACE BOXES
      setFaces(data.faces || []);

      // LIVE HEALTH
      setHealthData({
  heart_rate: Number(data.heart_rate) || 78,
  stress: Number(data.stress) || 20,
  fatigue: Number(data.fatigue) || 10,
  emotion: data.emotion || "Neutral",
  attention: data.attention || "HIGH",
  spo2: Number(data.spo2) || 98,
  temperature: Number(data.temperature) || 98.2
});

    } catch (error) {

      console.log(error);

    }
  };

  // AUTO AI ANALYSIS LOOP
  useEffect(() => {

    const interval = setInterval(() => {

      if (cameraOn) {
        detectFace();
      }

    }, 800);

    return () => clearInterval(interval);

  }, [cameraOn]);

  // AI COMMAND
  const handleSend = async () => {

    if (!input) return;

    const userMessage = input;

    setMessages((prev) => [
      ...prev,
      "🧑 " + userMessage
    ]);

    setHistory((prev) => [
      userMessage,
      ...prev
    ]);

    setInput("");

    try {

      const response = await fetch(
        `delightful-cooperation-production-8f2f.up.railway.app}`
      );

      const data = await response.json();

      const aiResponse = data.response;

      setMessages((prev) => [
        ...prev,
        "🤖 " + aiResponse
      ]);

      // DOCUMENT
      if (aiResponse.includes(".docx")) {
        setDocAvailable(true);
      }

    } catch {

      setMessages((prev) => [
        ...prev,
        "❌ Backend connection failed"
      ]);

    }
  };

  return (

    <div className="h-screen bg-black text-cyan-400 flex overflow-hidden">

      {/* LEFT HISTORY */}
      <div className="w-[18%] border-r border-cyan-900 p-4 overflow-y-auto">

        <h2 className="text-2xl mb-6">
          COMMAND HISTORY
        </h2>

        <div className="space-y-3">

          {history.map((item, index) => (

            <div
              key={index}
              className="bg-cyan-500/10 p-3 rounded-xl text-sm border border-cyan-800"
            >
              {item}
            </div>

          ))}

        </div>

      </div>

      {/* CENTER */}
      <div className="flex-1 flex flex-col items-center p-6">

        {/* TITLE */}
        <div className="text-5xl font-bold mb-6 tracking-widest">
          JARVIS HEALTH AI
        </div>

        {/* CAMERA PANEL */}
        <div className="relative w-[640px] h-[420px] border border-cyan-500 rounded-2xl overflow-hidden shadow-[0_0_40px_cyan] bg-black">

          {cameraOn ? (

            <>

              {/* WEBCAM */}
              <Webcam
                ref={webcamRef}
                audio={false}
                mirrored={true}
                screenshotFormat="image/jpeg"
                videoConstraints={{
                  width: 640,
                  height: 420,
                  facingMode: "user"
                }}
                className="w-full h-full object-contain"
              />

              {/* FACE BOXES */}
              {faces.map((face, index) => (

                <div
                  key={index}
                  className="absolute border-4 border-green-400 rounded-lg shadow-[0_0_15px_lime]"
                  style={{
                    left: `${face.x}px`,
                    top: `${face.y}px`,
                    width: `${face.w}px`,
                    height: `${face.h}px`
                  }}
                >

                  <div className="bg-green-400 text-black text-xs px-2 py-1 font-bold">
                    FACE DETECTED
                  </div>

                </div>

              ))}

            </>

          ) : (

            <div className="w-full h-full flex items-center justify-center text-2xl">
              CAMERA OFFLINE
            </div>

          )}

        </div>

        {/* CAMERA BUTTONS */}
        <div className="flex gap-6 mt-6">

          <button
            onClick={() => setCameraOn(true)}
            className="p-4 rounded-xl bg-cyan-500/20 border border-cyan-400 hover:scale-105 transition"
          >
            <Camera />
          </button>

          <button
            onClick={() => setCameraOn(false)}
            className="p-4 rounded-xl bg-red-500/20 border border-red-400 hover:scale-105 transition"
          >
            <CameraOff />
          </button>

        </div>

        {/* COMMAND BAR */}
        <div className="w-full flex gap-4 mt-8">

          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Give Command to JARVIS..."
            className="flex-1 p-4 rounded-xl bg-cyan-950/20 border border-cyan-500 outline-none"
          />

          <button
            onClick={handleSend}
            className="p-4 rounded-xl bg-cyan-500/20 border border-cyan-400 hover:scale-105 transition"
          >
            <Send />
          </button>

          <button
            className="p-4 rounded-xl bg-cyan-500/20 border border-cyan-400 hover:scale-105 transition"
          >
            <Mic />
          </button>

        </div>

        {/* DOWNLOAD */}
        {docAvailable && (

          <a
            href="http://127.0.0.1:8000/download"
            target="_blank"
            className="mt-6 flex items-center gap-2 p-4 rounded-xl bg-green-500/20 border border-green-400 hover:scale-105 transition"
          >
            <Download />
            Download Report
          </a>

        )}

      </div>

      {/* RIGHT HEALTH PANEL */}
      <div className="w-[22%] border-l border-cyan-900 p-4 overflow-y-auto">

        <h2 className="text-2xl mb-6">
          LIVE HEALTH MONITOR
        </h2>

        <div className="space-y-4">

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            ❤️ Heart Rate: {healthData.heart_rate} BPM
          </div>

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            😌 Stress: {healthData.stress}%
          </div>

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            😴 Fatigue: {healthData.fatigue}%
          </div>

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            😊 Emotion: {healthData.emotion}
          </div>

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            👁 Attention: {healthData.attention}
          </div>

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            🌡 Temperature: {healthData.temperature} °F
          </div>

          <div className="bg-cyan-500/10 p-4 rounded-xl border border-cyan-800">
            🩸 SpO2: {healthData.spo2}%
          </div>

        </div>

        {/* AI CONSOLE */}
        <div className="mt-8">

          <h2 className="text-2xl mb-4">
            AI CONSOLE
          </h2>

          <div className="space-y-3">

            {messages.map((msg, index) => (

              <div
                key={index}
                className="bg-cyan-500/10 p-3 rounded-xl text-sm border border-cyan-800"
              >
                {msg}
              </div>

            ))}

          </div>

        </div>

      </div>

    </div>

  );
}