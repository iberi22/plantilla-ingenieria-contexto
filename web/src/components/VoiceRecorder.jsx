import React, { useState, useRef } from 'react';
import { Mic, Square, Play, Pause, Globe, Video, Download, Edit, Image as ImageIcon, Check, Loader } from 'lucide-react';

function VoiceRecorder() {
  // Step 1: Recording
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [originalAudioPath, setOriginalAudioPath] = useState(null); // Path on server
  const [isPlaying, setIsPlaying] = useState(false);

  // Step 2: Transcription
  const [transcriptionStatus, setTranscriptionStatus] = useState('idle'); // idle, loading, success, error
  const [transcribedText, setTranscribedText] = useState('');
  const [detectedLanguage, setDetectedLanguage] = useState('');

  // Step 3: Translation
  const [selectedLanguages, setSelectedLanguages] = useState(['es']);
  const [translationStatus, setTranslationStatus] = useState('idle');
  const [translations, setTranslations] = useState({}); // { lang: text }

  // Step 4: Synthesis
  const [synthesisStatus, setSynthesisStatus] = useState({}); // { lang: 'idle' | 'loading' | 'success' | 'error' }
  const [synthesizedAudio, setSynthesizedAudio] = useState({}); // { lang: { url: string, path: string } }

  // Step 5: Images
  const [uploadedImages, setUploadedImages] = useState({}); // { id: { url: string, path: string, type: 'architecture' | 'flow' | 'screenshot' } }

  // Step 6: Video Generation
  const [videoStatus, setVideoStatus] = useState({}); // { lang: 'idle' | 'loading' | 'success' | 'error' }
  const [generatedVideos, setGeneratedVideos] = useState({}); // { lang: filename }

  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const chunksRef = useRef([]);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
    { code: 'pt', name: 'Português', flag: '🇵🇹' },
    { code: 'ru', name: 'Русский', flag: '🇷🇺' },
    { code: 'zh', name: '中文', flag: '🇨🇳' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ar', name: 'العربية', flag: '🇸🇦' },
  ];

  // --- Recording Functions ---

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        // Reset subsequent steps
        setTranscriptionStatus('idle');
        setTranscribedText('');
        setTranslations({});
        setSynthesizedAudio({});
        setGeneratedVideos({});
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Error: Could not access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // --- API Interactions ---

  const handleTranscribe = async () => {
    if (!audioBlob) return;

    setTranscriptionStatus('loading');
    const formData = new FormData();
    formData.append('audio', audioBlob, 'narration.wav');

    try {
      const response = await fetch('http://localhost:5000/api/transcribe', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      setTranscribedText(data.text);
      setDetectedLanguage(data.language);
      setOriginalAudioPath(data.audio_path);
      setTranscriptionStatus('success');
    } catch (error) {
      console.error('Transcription failed:', error);
      setTranscriptionStatus('error');
    }
  };

  const handleTranslate = async () => {
    if (!transcribedText || selectedLanguages.length === 0) return;

    setTranslationStatus('loading');
    try {
      const response = await fetch('http://localhost:5000/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: transcribedText,
          source_lang: detectedLanguage || 'en',
          target_langs: selectedLanguages
        }),
      });
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      setTranslations(data.translations);
      setTranslationStatus('success');
    } catch (error) {
      console.error('Translation failed:', error);
      setTranslationStatus('error');
    }
  };

  const handleSynthesize = async (lang) => {
    if (!translations[lang] || !originalAudioPath) return;

    setSynthesisStatus(prev => ({ ...prev, [lang]: 'loading' }));
    try {
      const response = await fetch('http://localhost:5000/api/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: translations[lang],
          language: lang,
          reference_audio: originalAudioPath
        }),
      });
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      setSynthesizedAudio(prev => ({
        ...prev,
        [lang]: {
          path: data.audio_path,
          url: `http://localhost:5000/api/download/${data.filename}`
        }
      }));
      setSynthesisStatus(prev => ({ ...prev, [lang]: 'success' }));
    } catch (error) {
      console.error(`Synthesis failed for ${lang}:`, error);
      setSynthesisStatus(prev => ({ ...prev, [lang]: 'error' }));
    }
  };

  const handleImageUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload-image', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      setUploadedImages(prev => ({
        ...prev,
        [type]: {
          path: data.path,
          url: URL.createObjectURL(file) // For local preview
        }
      }));
    } catch (error) {
      console.error('Image upload failed:', error);
      alert('Failed to upload image');
    }
  };

  const handleGenerateVideo = async (lang) => {
    if (!synthesizedAudio[lang]) return;

    setVideoStatus(prev => ({ ...prev, [lang]: 'loading' }));

    // Prepare images map for API
    const imagesMap = {};
    if (uploadedImages.architecture) imagesMap.architecture = uploadedImages.architecture.path;
    if (uploadedImages.flow) imagesMap.flow = uploadedImages.flow.path;
    if (uploadedImages.screenshot) imagesMap.screenshot = uploadedImages.screenshot.path;

    try {
      const response = await fetch('http://localhost:5000/api/generate-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_path: synthesizedAudio[lang].path,
          images: imagesMap,
          text_content: translations[lang],
          language: lang,
          repo_name: 'custom-project'
        }),
      });
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      setGeneratedVideos(prev => ({ ...prev, [lang]: data.filename }));
      setVideoStatus(prev => ({ ...prev, [lang]: 'success' }));
    } catch (error) {
      console.error(`Video generation failed for ${lang}:`, error);
      setVideoStatus(prev => ({ ...prev, [lang]: 'error' }));
    }
  };

  // --- UI Helpers ---

  const toggleLanguage = (langCode) => {
    setSelectedLanguages(prev =>
      prev.includes(langCode)
        ? prev.filter(l => l !== langCode)
        : [...prev, langCode]
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-2">
            🎙️ Voice Studio Pro
          </h1>
          <p className="text-gray-400">Record, Edit, Translate, and Create</p>
        </header>

        {/* 1. Recorder Section */}
        <section className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-xl">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm">1</span>
            Record Narration
          </h2>

          <div className="flex flex-col items-center gap-6">
            {!audioUrl ? (
              <button
                onClick={isRecording ? stopRecording : startRecording}
                className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                  isRecording
                    ? 'bg-red-600 hover:bg-red-700 animate-pulse shadow-lg shadow-red-900'
                    : 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-900'
                }`}
              >
                {isRecording ? <Square className="w-10 h-10" /> : <Mic className="w-10 h-10" />}
              </button>
            ) : (
              <div className="w-full max-w-md space-y-4">
                <audio ref={audioRef} src={audioUrl} onEnded={() => setIsPlaying(false)} className="hidden" />
                <div className="flex items-center gap-4 bg-gray-900 p-4 rounded-xl">
                  <button
                    onClick={togglePlayback}
                    className="w-12 h-12 rounded-full bg-green-600 hover:bg-green-700 flex items-center justify-center"
                  >
                    {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-1" />}
                  </button>
                  <div className="flex-1">
                    <div className="text-sm text-gray-400 mb-1">Recording Captured</div>
                    <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 w-full animate-pulse"></div>
                    </div>
                  </div>
                  <button
                    onClick={() => { setAudioUrl(null); setAudioBlob(null); }}
                    className="text-gray-400 hover:text-white"
                  >
                    Reset
                  </button>
                </div>

                <button
                  onClick={handleTranscribe}
                  disabled={transcriptionStatus === 'loading'}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {transcriptionStatus === 'loading' ? <Loader className="animate-spin w-5 h-5" /> : <Edit className="w-5 h-5" />}
                  Transcribe Audio
                </button>
              </div>
            )}
            <p className="text-sm text-gray-400">
              {isRecording ? 'Recording in progress...' : !audioUrl ? 'Click to start recording' : ''}
            </p>
          </div>
        </section>

        {/* 2. Transcription Section */}
        {transcriptionStatus !== 'idle' && (
          <section className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-xl animate-in fade-in slide-in-from-bottom-4">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm">2</span>
              Review Transcription
            </h2>

            <div className="space-y-4">
              <div className="bg-gray-900 p-4 rounded-xl border border-gray-700">
                <label className="text-xs text-gray-500 uppercase font-semibold block mb-2">Detected Language: {detectedLanguage}</label>
                <textarea
                  value={transcribedText}
                  onChange={(e) => setTranscribedText(e.target.value)}
                  className="w-full bg-transparent border-none text-gray-200 focus:ring-0 resize-none h-32"
                  placeholder="Transcription will appear here..."
                />
              </div>

              <div className="flex flex-col gap-4">
                 <h3 className="font-medium text-gray-300">Select Target Languages:</h3>
                 <div className="flex flex-wrap gap-2">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => toggleLanguage(lang.code)}
                      className={`px-3 py-1.5 rounded-lg border transition-all flex items-center gap-2 ${
                        selectedLanguages.includes(lang.code)
                          ? 'border-blue-500 bg-blue-900/40 text-blue-200'
                          : 'border-gray-600 bg-gray-800 hover:border-gray-500'
                      }`}
                    >
                      <span>{lang.flag}</span>
                      <span className="text-sm">{lang.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleTranslate}
                disabled={translationStatus === 'loading' || selectedLanguages.length === 0}
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {translationStatus === 'loading' ? <Loader className="animate-spin w-5 h-5" /> : <Globe className="w-5 h-5" />}
                Translate Text
              </button>
            </div>
          </section>
        )}

        {/* 3. Translation & Synthesis Section */}
        {translationStatus === 'success' && (
          <section className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-xl animate-in fade-in slide-in-from-bottom-4">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <span className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm">3</span>
              Translations & Voice Synthesis
            </h2>

            <div className="grid gap-6">
              {selectedLanguages.map(lang => (
                <div key={lang} className="bg-gray-900 rounded-xl p-4 border border-gray-700">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="flex items-center gap-2 font-medium">
                      {languages.find(l => l.code === lang)?.flag}
                      {languages.find(l => l.code === lang)?.name}
                    </h3>
                  </div>

                  <textarea
                    value={translations[lang] || ''}
                    onChange={(e) => setTranslations(prev => ({...prev, [lang]: e.target.value}))}
                    className="w-full bg-gray-800 rounded-lg p-3 text-sm text-gray-200 border border-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 mb-4 h-24"
                  />

                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => handleSynthesize(lang)}
                      disabled={synthesisStatus[lang] === 'loading'}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50"
                    >
                      {synthesisStatus[lang] === 'loading' ? <Loader className="animate-spin w-4 h-4" /> : <Mic className="w-4 h-4" />}
                      Synthesize Voice
                    </button>

                    {synthesizedAudio[lang] && (
                      <audio controls src={synthesizedAudio[lang].url} className="h-8 w-64" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 4. Visuals & Generation */}
        {Object.keys(synthesizedAudio).length > 0 && (
          <section className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-xl animate-in fade-in slide-in-from-bottom-4">
             <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <span className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm">4</span>
              Add Visuals & Generate
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {['architecture', 'flow', 'screenshot'].map(type => (
                <div key={type} className="bg-gray-900 p-4 rounded-xl border border-gray-700 flex flex-col items-center">
                  <div className="w-full aspect-video bg-gray-800 rounded-lg mb-3 flex items-center justify-center overflow-hidden relative group">
                    {uploadedImages[type] ? (
                      <img src={uploadedImages[type].url} alt={type} className="w-full h-full object-cover" />
                    ) : (
                      <ImageIcon className="text-gray-600 w-8 h-8" />
                    )}
                    <label className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                      <span className="text-xs font-medium bg-white/20 backdrop-blur px-2 py-1 rounded">Change</span>
                      <input type="file" accept="image/*" className="hidden" onChange={(e) => handleImageUpload(e, type)} />
                    </label>
                  </div>
                  <span className="text-sm text-gray-400 capitalize">{type} Image</span>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-700 pt-6">
              <h3 className="text-lg font-medium mb-4">Generate Final Videos</h3>
              <div className="space-y-3">
                {Object.keys(synthesizedAudio).map(lang => (
                  <div key={lang} className="flex items-center justify-between bg-gray-900 p-3 rounded-xl border border-gray-700">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{languages.find(l => l.code === lang)?.flag}</span>
                      <span className="font-medium text-gray-300">{languages.find(l => l.code === lang)?.name}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      {generatedVideos[lang] ? (
                        <a
                          href={`http://localhost:5000/api/download/${generatedVideos[lang]}`}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium flex items-center gap-2"
                        >
                          <Download className="w-4 h-4" />
                          Download Video
                        </a>
                      ) : (
                        <button
                          onClick={() => handleGenerateVideo(lang)}
                          disabled={videoStatus[lang] === 'loading'}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50"
                        >
                          {videoStatus[lang] === 'loading' ? <Loader className="animate-spin w-4 h-4" /> : <Video className="w-4 h-4" />}
                          Generate Video
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

      </div>
    </div>
  );
}

export default VoiceRecorder;
